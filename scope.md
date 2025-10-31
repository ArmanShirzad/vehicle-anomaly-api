# Project Scope and Purpose

## What This Project Is

A production-ready **Machine Learning API** for vehicle anomaly detection. It combines:

- **Python/FastAPI** - High-performance async web framework
- **scikit-learn Isolation Forest** - ML-powered anomaly detection
- **AWS Fargate** - Serverless container deployment (no servers to manage)
- **AWS CDK** - Infrastructure as Code (deploy everything with a few commands)
- **OpenTelemetry + Prometheus** - Observability and monitoring
- **JWT Authentication** - Secure API access
- **Rate Limiting** - Prevent API abuse
- **PostgreSQL** - Persistent data storage
- **Model Versioning** - Track and rollback ML models

In simple terms: **Train anomaly detection models with telemetry data, then score real-time vehicle data to identify abnormalities.**

## What You Get

### API Endpoints
- `POST /ingest` - Train/update anomaly detection models with telemetry batches
- `POST /score` - Get anomaly predictions for real-time telemetry data
- `GET /health`, `/health/ready`, `/healthz` - Health monitoring endpoints
- Auto-generated Swagger docs at `/docs`

### ML Capabilities
- **Isolation Forest** algorithm (200 estimators, 5% contamination default)
- **Model versioning** with automatic timestamps
- **Decision scores** (how anomalous) + **Binary predictions** (is anomaly)
- **Persistent storage** with S3 or local filesystem

### AWS Infrastructure (Deployed by CDK)
- **Application Load Balancer** - Public HTTP/HTTPS access
- **Fargate Tasks** - Auto-scaling containers (1-4 instances)
- **Auto-scaling** - Scale based on CPU usage (60% threshold)
- **CloudWatch Logs** - Centralized logging
- **X-Ray Tracing** - Distributed request tracing
- **Prometheus Metrics** - Performance monitoring
- **VPC & Security** - Network isolation and security groups

### Developer Experience
- **Single command deployment** - `cdk deploy`
- **Local development** - `uvicorn app.main:app --reload`
- **Test suite** - Pytest with fixtures
- **Type hints** - Full Python type safety
- **Documentation** - Auto-generated API docs

## Simple Flow

```
Your Python App (app/main.py)
    ↓
FastAPI Server (Training + Scoring ML Models)
    ↓
Docker Container
    ↓  
AWS Fargate (Serverless Container Service)
    ↓
Application Load Balancer (Public URL)
    ↓
Auto-scaling (1-4 instances based on CPU)
    ↓
Anyone can access it via HTTP/HTTPS
```

## Quick Start

### With AWS CDK (Requires AWS Credentials)

```bash
# 1. Install CDK dependencies
pip install -r deploy/cdk/requirements.txt

# 2. Bootstrap AWS CDK (first time only)
cd deploy/cdk && cdk bootstrap

# 3. Deploy everything
cdk deploy
```

That's it. AWS provisions: VPC, load balancer, containers, autoscaling, monitoring, logs, and tracing.

### CI/CD Pipeline

The GitHub Actions workflow automatically:
- Builds and pushes Docker image on every push to `main`
- Deploys to AWS only if `AWS_DEPLOY_ROLE_ARN` secret is configured
- Pipeline succeeds without AWS credentials (skips deployment gracefully)

### Alternative: Deploy to Render/Railway (No AWS Required)

1. Connect GitHub repo to Render/Railway
2. Auto-detects Dockerfile
3. Set `USE_LOCAL_STORAGE=true` environment variable
4. Deploy - no AWS credentials needed

## What This Solves

Problem scenarios:
- "I need to deploy a ML-powered Python API to production"
- "I want it to scale automatically when traffic increases"
- "I want comprehensive monitoring and observability"
- "I want to deploy with a single command"
- "I need to track different versions of my ML models"
- "I want enterprise security (JWT auth, rate limiting)"

Real-world use case: Vehicle telemetry monitoring
- Fleet operators collect telemetry data from vehicles
- API trains anomaly detection models on historical data
- Real-time scoring identifies unusual patterns (engine issues, sensor failures, etc.)
- Auto-scaling handles traffic spikes
- CloudWatch/X-Ray helps debug issues in production

## Technical Stack

**Backend**: FastAPI, SQLAlchemy (async), PostgreSQL  
**ML**: scikit-learn, Isolation Forest, joblib  
**Deployment**: Docker, AWS Fargate, ALB  
**Infrastructure**: AWS CDK (Python), CloudFormation  
**Observability**: OpenTelemetry, Prometheus, CloudWatch, X-Ray  
**Security**: JWT tokens, rate limiting, CORS  
**Testing**: pytest, FastAPI TestClient  

## Not Included (Out of Scope)

- **Frontend UI** - This is a pure API backend, no web interface
- **External data pipelines** - No Kafka, Kinesis, or event streaming (data sent directly via REST API)
- **Data warehouse integration** - No Redshift, Snowflake, or data lake connectivity
- **User management system** - JWT tokens are verified but no user registration/login endpoints
- **Advanced ML features** - No hyperparameter tuning, A/B testing, or multi-model ensembling
- **Batch processing** - No scheduled jobs or background workers for large datasets

