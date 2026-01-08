# GCP Cloud Run Deployment Guide

## Prerequisites

1. Google Cloud account with billing enabled
2. gcloud CLI installed: https://cloud.google.com/sdk/docs/install
3. Docker installed locally (optional, for testing)

## Setup

### 1. Initialize GCP Project

```bash
# Login to GCP
gcloud auth login

# Create new project (or use existing)
gcloud projects create hk-healthcare-rag --name="HK Healthcare RAG"

# Set project
gcloud config set project hk-healthcare-rag

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Build and Test Locally (Optional)

```bash
# Build Docker image
docker build -t hk-healthcare-rag:local .

# Test locally
docker run -p 8080:8080 hk-healthcare-rag:local

# Test API
curl http://localhost:8080/health
```

### 3. Deploy to Cloud Run

**Option A: Using Cloud Build (Recommended)**

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml

# Get service URL
gcloud run services describe hk-healthcare-rag --region=asia-east2 --format='value(status.url)'
```

**Option B: Manual Deploy**

```bash
# Build and push image
gcloud builds submit --tag gcr.io/hk-healthcare-rag/app

# Deploy to Cloud Run
gcloud run deploy hk-healthcare-rag \
  --image gcr.io/hk-healthcare-rag/app \
  --region asia-east2 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### 4. Test Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe hk-healthcare-rag --region=asia-east2 --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test query
curl -X POST "$SERVICE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many doctors in Hong Kong?"}'
```

## Cost Optimization

**Cloud Run Pricing (as of Jan 2026)**:
- Free tier: 2 million requests/month
- CPU: $0.00002400/vCPU-second (only when handling requests)
- Memory: $0.00000250/GB-second
- Requests: $0.40 per million requests

**Estimated monthly cost** (assuming 1000 queries/day, 5s avg latency):
- CPU: ~$7.20
- Memory: ~$6.00
- Requests: ~$0.01
- **Total: ~$13.21/month**

**Scaling to zero**: Cloud Run scales to zero when idle = $0 cost when not in use!

## Monitoring

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=hk-healthcare-rag" --limit 50
```

### View Metrics
```bash
# Check service metrics
gcloud run services describe hk-healthcare-rag --region=asia-east2

# Access metrics endpoint
curl $SERVICE_URL/metrics
```

### Set Up Alerts (Optional)
```bash
# Create alert for error rate > 5%
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="RAG Error Rate Alert" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=60s
```

## Troubleshooting

**Container fails to start:**
- Check logs: `gcloud logging read --limit 100`
- Verify Ollama installation in Dockerfile
- Increase memory/CPU if needed

**Slow responses:**
- Increase CPU allocation (currently 2 vCPUs)
- Consider using smaller LLM model
- Optimize vector search (reduce `k` value)

**High costs:**
- Set max instances lower (currently 10)
- Reduce timeout (currently 300s)
- Add request caching

## Update Deployment

```bash
# Rebuild and redeploy
gcloud builds submit --config cloudbuild.yaml

# Or quick update (same image)
gcloud run services update hk-healthcare-rag --region=asia-east2
```

## Delete Deployment

```bash
# Delete Cloud Run service
gcloud run services delete hk-healthcare-rag --region=asia-east2

# Delete container images
gcloud container images delete gcr.io/hk-healthcare-rag/app --quiet
```

---

**Your service will be live at**: `https://hk-healthcare-rag-RANDOM.a.run.app`
