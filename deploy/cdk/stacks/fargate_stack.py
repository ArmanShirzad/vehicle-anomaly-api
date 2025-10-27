"""CDK stack provisioning the vehicle anomaly API on AWS Fargate."""

from __future__ import annotations

from textwrap import dedent

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_certificatemanager as acm,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct


class VehicleAnomalyFargateStack(Stack):
    """Deploy the API behind an application load balancer on AWS Fargate."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "Vpc", max_azs=2)

        image_uri = self.node.try_get_context("image_uri") or "ghcr.io/armanshirzad/vehicle-anomaly-api:latest"
        container_port = int(self.node.try_get_context("container_port") or 8000)

        execution_role = iam.Role(
            self,
            "ExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"),
            ],
        )

        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
        )

        log_group = logs.LogGroup(
            self,
            "ServiceLogs",
            retention=logs.RetentionDays.ONE_WEEK,
            log_group_name="/aws/ecs/vehicle-anomaly-api",
            removal_policy=RemovalPolicy.RETAIN,
        )

        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "VehicleAnomalyService",
            vpc=vpc,
            public_load_balancer=True,
            assign_public_ip=True,
            cpu=256,
            memory_limit_mib=512,
            desired_count=int(self.node.try_get_context("desired_count") or 2),
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(image_uri),
                container_port=container_port,
                environment={
                    "ENVIRONMENT": self.node.try_get_context("environment") or "prod",
                },
                task_role=task_role,
                execution_role=execution_role,
                log_driver=ecs.AwsLogDriver(stream_prefix="api", log_group=log_group),
            ),
            health_check_grace_period=Duration.seconds(60),
        )

        service.target_group.configure_health_check(path="/healthz", healthy_http_codes="200")

        scalable_target = service.service.auto_scale_task_count(
            min_capacity=int(self.node.try_get_context("min_capacity") or 1),
            max_capacity=int(self.node.try_get_context("max_capacity") or 4),
        )
        scalable_target.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=60,
            scale_in_cooldown=Duration.minutes(2),
            scale_out_cooldown=Duration.minutes(1),
        )

        _collector_container = service.task_definition.add_container(
            "AdotCollector",
            image=ecs.ContainerImage.from_registry(
                self.node.try_get_context("adot_image")
                or "public.ecr.aws/aws-observability/aws-otel-collector:latest"
            ),
            essential=True,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="adot", log_group=log_group),
            environment={
                "AWS_REGION": Stack.of(self).region,
                "AOT_CONFIG_CONTENT": dedent(
                    """
                    receivers:
                      otlp:
                        protocols:
                          grpc:
                            endpoint: 0.0.0.0:4317
                    processors:
                      batch: {}
                    exporters:
                      awsxray: {}
                      awsemf: {}
                    service:
                      pipelines:
                        traces:
                          receivers: [otlp]
                          processors: [batch]
                          exporters: [awsxray]
                        metrics:
                          receivers: [otlp]
                          processors: [batch]
                          exporters: [awsemf]
                    """
                ).strip(),
            },
            port_mappings=[ecs.PortMapping(container_port=4317, host_port=4317, protocol=ecs.Protocol.TCP)],
        )

        certificate_arn = self.node.try_get_context("certificate_arn")
        if certificate_arn:
            certificate = acm.Certificate.from_certificate_arn(self, "AlbCertificate", certificate_arn)
            https_listener = service.load_balancer.add_listener(
                "HttpsListener",
                port=443,
                certificates=[certificate],
                open=True,
                protocol=elbv2.ApplicationProtocol.HTTPS,
            )
            https_listener.add_targets(
                "HttpsTargets",
                port=container_port,
                targets=[service.service],
                health_check=elbv2.HealthCheck(path="/healthz", healthy_http_codes="200"),
            )

        service.load_balancer.connections.allow_from_any_ipv4(ec2.Port.tcp(443), "Allow HTTPS inbound")
        service.load_balancer.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Allow HTTP inbound")

