# Vehicle Anomaly API - Virtual Environment

## How to Run the Application

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Start the Server
```bash
uvicorn app.main:app --reload
```

### 3. Test the Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/health/ready

# Liveness probe
curl http://localhost:8000/healthz
```

## Manual Steps Remaining

### Step 3: Database Setup (Required for database features)
1. Install PostgreSQL
2. Create database: `CREATE DATABASE vehicleapi;`
3. Update `.env` with `DATABASE_URL`

### Step 4: AWS/S3 Setup (Optional, for cloud storage)
1. Create S3 bucket: `aws s3 mb s3://your-bucket-name`
2. Update `.env` with S3 settings
3. Configure AWS credentials: `aws configure`

## All Critical Gaps Implemented!

✅ Database Integration (with async SQLAlchemy)
✅ JWT Authentication (ready to use)
✅ Rate Limiting (60 req/min default)
✅ S3 Storage Support
✅ Enhanced CORS Configuration
✅ Input Validation
✅ Configuration Management

The application is ready to use!
