#!/bin/bash

# End-to-End Test Script for Vehicle Anomaly API
# This script tests all functionality of the API

set -e  # Exit on any error

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "   End-to-End Test Suite"
echo "   Vehicle Anomaly Detection API"
echo "=========================================="
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "Response: $body"
else
    echo -e "${RED}✗ Health check failed (HTTP $http_code)${NC}"
    echo "Response: $body"
    exit 1
fi
echo ""

# Test 2: Readiness Check
echo -e "${YELLOW}Test 2: Readiness Check${NC}"
response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health/ready")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Readiness check passed${NC}"
    echo "Response: $body"
else
    echo -e "${RED}✗ Readiness check failed (HTTP $http_code)${NC}"
    echo "Response: $body"
fi
echo ""

# Test 3: Liveness Probe
echo -e "${YELLOW}Test 3: Liveness Probe${NC}"
response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/healthz")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Liveness probe passed${NC}"
    echo "Response: $body"
else
    echo -e "${RED}✗ Liveness probe failed (HTTP $http_code)${NC}"
    echo "Response: $body"
    exit 1
fi
echo ""

# Test 4: Train Model (POST /ingest)
echo -e "${YELLOW}Test 4: Train Anomaly Detection Model${NC}"
INGEST_PAYLOAD='{
  "records": [
    {
      "vehicle_id": "VH-001",
      "timestamp": "2024-01-15T10:00:00Z",
      "feature_vector": [0.5, 0.3, 0.8, 1.2, 0.9]
    },
    {
      "vehicle_id": "VH-002",
      "timestamp": "2024-01-15T10:01:00Z",
      "feature_vector": [0.6, 0.25, 0.75, 1.0, 0.85]
    },
    {
      "vehicle_id": "VH-003",
      "timestamp": "2024-01-15T10:02:00Z",
      "feature_vector": [0.4, 0.35, 0.85, 1.3, 1.1]
    }
  ]
}'

response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d "$INGEST_PAYLOAD" \
  "${BASE_URL}/ingest")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ Model training passed${NC}"
    echo "Response: $body"
    MODEL_VERSION=$(echo "$body" | grep -o '"model_version":"[^"]*"' | cut -d'"' -f4)
    echo "Model Version: $MODEL_VERSION"
else
    echo -e "${RED}✗ Model training failed (HTTP $http_code)${NC}"
    echo "Response: $body"
    exit 1
fi
echo ""

# Test 5: Score Telemetry (POST /score)
echo -e "${YELLOW}Test 5: Score Telemetry for Anomalies${NC}"
SCORE_PAYLOAD='{
  "vehicle_id": "VH-004",
  "timestamp": "2024-01-15T10:05:00Z",
  "feature_vector": [0.7, 0.2, 0.9, 0.5, 0.75]
}'

response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d "$SCORE_PAYLOAD" \
  "${BASE_URL}/score")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Anomaly scoring passed${NC}"
    echo "Response: $body"
    ANOMALY_STATUS=$(echo "$body" | grep -o '"is_anomaly":[^,]*' | cut -d':' -f2)
    ANOMALY_SCORE=$(echo "$body" | grep -o '"anomaly_score":[^,]*' | cut -d':' -f2)
    echo "Anomaly Status: $ANOMALY_STATUS"
    echo "Anomaly Score: $ANOMALY_SCORE"
else
    echo -e "${RED}✗ Anomaly scoring failed (HTTP $http_code)${NC}"
    echo "Response: $body"
    exit 1
fi
echo ""

# Test 6: Score with Anomalous Data
echo -e "${YELLOW}Test 6: Score Anomalous Telemetry${NC}"
ANOMALOUS_PAYLOAD='{
  "vehicle_id": "VH-005",
  "timestamp": "2024-01-15T10:06:00Z",
  "feature_vector": [10.0, 15.0, 20.0, 5.0, 25.0]
}'

response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d "$ANOMALOUS_PAYLOAD" \
  "${BASE_URL}/score")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Anomalous data scoring passed${NC}"
    echo "Response: $body"
    ANOMALY_STATUS=$(echo "$body" | grep -o '"is_anomaly":[^,]*' | cut -d':' -f2)
    echo "Anomaly Detected: $ANOMALY_STATUS"
else
    echo -e "${RED}✗ Anomalous data scoring failed (HTTP $http_code)${NC}"
    echo "Response: $body"
fi
echo ""

# Test 7: Metrics Endpoint
echo -e "${YELLOW}Test 7: Prometheus Metrics${NC}"
response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/metrics")
http_code=$(echo "$response" | tail -n1)
metrics_count=$(echo "$response" | head -nmetrics_count=$(echo "$response" | wc -l))

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Metrics endpoint accessible${NC}"
    echo "Metrics lines: $(wc -l <<< "$response")"
else
    echo -e "${RED}✗ Metrics endpoint failed (HTTP $http_code)${NC}"
fi
echo ""

# Test 8: API Documentation
echo -e "${YELLOW}Test 8: API Documentation${NC}"
response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/docs")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ API documentation accessible${NC}"
else
    echo -e "${RED}✗ API documentation failed (HTTP $http_code)${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}All End-to-End Tests Passed!${NC}"
echo "=========================================="

