# Vehicle Anomaly API

A FastAPI-based microservice for vehicle telemetry anomaly detection using Isolation Forest models.

## Features

- Anomaly detection using scikit-learn's Isolation Forest
- RESTful API for training and scoring telemetry data
- OpenTelemetry instrumentation for observability
- AWS Fargate deployment via CDK
- Comprehensive test suite

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

The application can be deployed to AWS Fargate using the included CDK stack:

```bash
cd deploy/cdk
cdk synth
cdk deploy
```

## License

MIT
