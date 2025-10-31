# Vehicle Anomaly API

A FastAPI-based microservice for vehicle telemetry anomaly detection using Isolation Forest models.

## Features

- Anomaly detection using scikit-learn's Isolation Forest
- RESTful API for training and scoring telemetry data
- OpenTelemetry instrumentation for observability
- AWS Fargate deployment via CDK
- Comprehensive test suite

## Big Picture & Architecture

### Overview

The Vehicle Anomaly API is a microservice that detects anomalies in vehicle telemetry data using machine learning. It provides a RESTful interface for training anomaly detection models and scoring telemetry records in real-time.

### Key Components

1. **API Layer** (`app/api/routes/`)
   - Health endpoints for monitoring
   - Ingest endpoint for model training
   - Score endpoint for anomaly detection

2. **Domain Models** (`app/domain/`)
   - TelemetryRecord: Individual vehicle data points
   - TelemetryBatch: Training data sets
   - Model metadata and responses

3. **Scoring Service** (`app/services/`)
   - Isolation Forest model management
   - Model versioning and artifact storage
   - Training and prediction logic

4. **Observability** (`app/instrumentation/`)
   - OpenTelemetry tracing
   - Prometheus metrics
   - CloudWatch integration

5. **Infrastructure** (`deploy/cdk/`)
   - AWS Fargate container deployment
   - Load balancer with auto-scaling
   - Container orchestration

### Workflow

#### Model Training Flow
```
Client → POST /ingest → ScoringService
                              ↓
                        Train IsolationForest
                              ↓
                        Save model artifact
                              ↓
                        Return model version
```

1. Client sends telemetry batch via `POST /ingest`
2. Service extracts feature vectors from telemetry records
3. Isolation Forest model is trained on the data
4. Model is persisted to disk with versioning
5. Metadata and model version are returned to client

#### Anomaly Detection Flow
```
Client → POST /score → ScoringService
                              ↓
                        Load model by version
                              ↓
                        Compute anomaly score
                              ↓
                        Return prediction + score
```

1. Client sends telemetry record via `POST /score`
2. Service loads the specified (or latest) model version
3. Feature vector is scored for anomalies
4. Returns anomaly flag + decision score

### System Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP/REST
       ↓
┌─────────────────────────────────────┐
│         Load Balancer               │
│      (Health: /healthz)             │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│      Fargate Container              │
│  ┌──────────────────────────────┐  │
│  │  FastAPI Application          │  │
│  │  ├─ Health Endpoints          │  │
│  │  ├─ Ingest Endpoint            │  │
│  │  └─ Score Endpoint             │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Scoring Service              │  │
│  │  ├─ IsolationForest           │  │
│  │  └─ Model Storage              │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  OpenTelemetry Collector       │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
       │
       ↓
┌──────────────┬──────────────┐
│   CloudWatch │    X-Ray     │
│   (Logs)     │  (Traces)    │
└──────────────┴──────────────┘
```

### Data Flow Example

**Training:**
```json
POST /ingest
{
  "records": [
    {
      "vehicle_id": "VH-001",
      "timestamp": "2024-01-15T10:00:00Z",
      "feature_vector": [0.5, 0.3, 0.8, 1.2]
    }
  ]
}
→ Returns: {"model_version": "20240115100000", "record_count": 1}
```

**Scoring:**
```json
POST /score
{
  "vehicle_id": "VH-002",
  "timestamp": "2024-01-15T10:05:00Z",
  "feature_vector": [0.7, 0.2, 0.9, 0.5]
}
→ Returns: {
    "vehicle_id": "VH-002",
    "anomaly_score": -0.15,
    "is_anomaly": false,
    "model_version": "20240115100000"
  }
```

## API Endpoints

- `POST /ingest` - Train or update an anomaly detection model
- `POST /score` - Score telemetry data for anomalies
- `GET /health` - Health check endpoint
- `GET /health/ready` - Readiness probe
- `GET /healthz` - Liveness probe

## Setup

### Requirements

- Python 3.12+
- pip
- Docker

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the application
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest
```

## Deployment

### CI/CD Pipeline

The repository includes a GitHub Actions workflow (`.github/workflows/deploy-aws.yml`) that automatically:

1. **Builds and pushes Docker images** to GitHub Container Registry (GHCR) on every push to `main`
2. **Deploys to AWS Fargate** if AWS credentials are configured (optional)

**Workflow Behavior:**
- **Always runs**: Docker image build and push to GHCR
- **Conditional**: AWS deployment (only if `AWS_DEPLOY_ROLE_ARN` secret is configured)
- **Pipeline passes** even without AWS credentials (AWS steps are skipped gracefully)

**To enable AWS deployment:**
1. Configure `AWS_DEPLOY_ROLE_ARN` secret in GitHub repository settings
2. Set up IAM OIDC provider for GitHub Actions in AWS
3. The workflow will automatically deploy on the next push

### Manual Deployment

You can also deploy manually using the CDK stack:

```bash
cd deploy/cdk
cdk synth
cdk deploy
```

**Note:** For local development and demos, you can deploy to alternative platforms (Render, Railway, Fly.io) without any code changes - the application uses local storage by default.

## Development Status

### Completed

- Core API endpoints (ingest, score, health)
- Isolation Forest model implementation
- OpenTelemetry instrumentation
- Prometheus metrics
- AWS Fargate CDK stack
- Comprehensive test suite
- Model versioning system

### Missing / Incomplete

1. **Database Integration**: `app/core/database.py` is stubbed - needs actual database connection
2. **Authentication**: No authentication/authorization implemented
3. **API Documentation**: Missing example requests and OpenAPI documentation
4. **Model Persistence**: Models stored locally - need S3 or EFS for production
5. **Error Handling**: Basic error handling needs improvement
6. **Rate Limiting**: No rate limiting on endpoints
7. **CORS Configuration**: Not fully configured
8. **Environment Variables**: No `.env` example file
9. **CI/CD Pipeline**: GitHub Actions workflow exists but needs secrets configured
10. **Logging**: Basic logging implemented, needs structured logging
11. **Monitoring**: CloudWatch/X-Ray integration incomplete

### Recommended Next Steps

1. Add database connection pooling and migrations
2. Implement authentication (JWT or OAuth2)
3. Add request validation and input sanitization
4. Set up persistent storage for models (S3/EFS)
5. Add comprehensive error handling
6. Configure rate limiting
7. Add structured logging with correlation IDs
8. Set up monitoring dashboards
9. Add integration tests
10. Document deployment process

## AWS Deployment

This project demonstrates expertise in:
- **AWS Fargate**: Container orchestration
- **AWS CDK**: Infrastructure as Code
- **S3**: Model artifact storage
- **Application Load Balancer**: High availability
- **Auto-scaling**: Horizontal scaling based on CPU
- **CloudWatch**: Logging and monitoring
- **X-Ray**: Distributed tracing

Deploy to AWS using the included CDK stack:
```bash
cd deploy/cdk
cdk synth
cdk deploy
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_scoring.py -v
```

## License

MIt
