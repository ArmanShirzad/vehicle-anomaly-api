#!/usr/bin/env python3
"""CDK application entrypoint for the vehicle anomaly API."""

from __future__ import annotations

from aws_cdk import App, Environment

from stacks.fargate_stack import VehicleAnomalyFargateStack

app = App()

account = app.node.try_get_context("account")
region = app.node.try_get_context("region")
stack_env = Environment(account=account, region=region) if account or region else None

VehicleAnomalyFargateStack(app, "VehicleAnomalyFargate", env=stack_env)

app.synth()

