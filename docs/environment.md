# ENVIRONMENT SETUP GUIDE

## 1. LOCAL DEVELOPMENT SETUP

### Prerequisites

```bash
# Required tools
- Python 3.11+
- Docker Desktop
- Google Cloud SDK
- Git

# Verification
python --version  # 3.11+
docker --version
gcloud --version
```

### Installation

```bash
# Clone repo
git clone https://github.com/pacc-admin/data-sync-custom.git
cd data-sync-custom

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements-cloud.txt

# Copy environment template
cp .env.example .env
# Edit .env with your local settings
```

### Local Testing with Docker

```bash
# Build Docker image
docker build -t data-sync-custom:dev .

# Run container locally
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=pacc-raw-data \
  -e LOG_LEVEL=DEBUG \
  -v $(pwd):/app \
  data-sync-custom:dev

# Test endpoints
curl -X GET http://localhost:8080/health
curl -X POST http://localhost:8080/sync/base-vn
```

---

## 2. GOOGLE CLOUD SETUP

### 2.1 Initial Setup

```bash
# Initialize gcloud
gcloud init

# Set default project
gcloud config set project pacc-raw-data

# Verify
gcloud config list
```

### 2.2 Enable APIs

```bash
# Enable required services
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudbuilder.googleapis.com \
  artifactregistry.googleapis.com

# Verify
gcloud services list --enabled | grep -E "run|scheduler|secret"
```

### 2.3 Create Service Account

```bash
# Create service account
gcloud iam service-accounts create data-sync-custom \
  --display-name="Data Sync Custom Service" \
  --description="Service account for data sync to BigQuery"

# Get service account email (needed later)
ACCOUNT=$(gcloud iam service-accounts list --filter="displayName:Data\ Sync" \
  --format="value(email)")
echo $ACCOUNT  # data-sync-custom@pacc-raw-data.iam.gserviceaccount.com
```

### 2.4 Grant IAM Permissions

```bash
PROJECT_ID="pacc-raw-data"
ACCOUNT="data-sync-custom@${PROJECT_ID}.iam.gserviceaccount.com"

# BigQuery permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${ACCOUNT}" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${ACCOUNT}" \
  --role="roles/bigquery.jobUser"

# Secret Manager permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

# Cloud Logging permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${ACCOUNT}" \
  --role="roles/logging.logWriter"

# Verify
gcloud projects get-iam-policy ${PROJECT_ID} \
  --flatten="bindings[].members" \
  --filter="bindings.members:${ACCOUNT}"
```

---

## 3. SECRET MANAGEMENT

### 3.1 Create Secrets

#### Base.vn API Tokens

```bash
# Create secret with JSON format
gcloud secrets create base-vn-tokens --replication-policy="automatic"

# Add secret version with token data
echo '{
  "hrm": "7383-SRGCCB22PNT8Y7A47M9HYQNXUVGFDBWVNQ2BVH3WLQUS2RD83Q5YD4CSB79XXS3G-LKSK5HRBSNPS3235ZQBR5QD92FM5EFALVCWLKHCCK22EXGJ8D2YS8CJVB2HDYYZ8",
  "payroll": "7383-HCMUFGYR35XWJDCKFCJ93VNFN89F4PR5H2ALD63V9CCJZXQ948PRBE6BDNJUX29H-YDN58WMY5JWFGPW2EKEXJLJ5PHUH9HKKJDNAX3VCQDGZP4WT55NVR964J6ZAA5WQ",
  "hiring": "7383-HRQ98383DUWSAN4DT433FJYDNMQWTBA3RECR33LSDTX7K44UL7Q6EX66XX76HBB9-FCR54BP4UVY7XTXSWXRS67ESTXH6KUZB6SLSQEWCBA4RS4H3ZHPHMLUQ36MBTCYL",
  "account": "7383-FVHGUV7XV8XYMS7ELKG2MA7N6GP4TLQDPLTAR253PS9EB6FZDQBHAL2J3E47UZB9-KJC3ABQMLDGMEBW7B2PUTK45RDX6YUZ32RYWZUNDAPTVG4ZPHH8TBUJYDS35AXH9"
}' | gcloud secrets versions add base-vn-tokens --data-file=-

# Verify
gcloud secrets versions list base-vn-tokens
```

#### MSSQL Connection

```bash
gcloud secrets create mssql-connection --replication-policy="automatic"

echo '{
  "server": "your-mssql-server.database.windows.net",
  "username": "your-username",
  "password": "your-password",
  "port": 1433,
  "encrypt": true,
  "trustServerCertificate": true
}' | gcloud secrets versions add mssql-connection --data-file=-
```

#### WorldFone API Key

```bash
gcloud secrets create worldfone-key --replication-policy="automatic"

echo "your-api-key-here" | gcloud secrets versions add worldfone-key --data-file=-
```

### 3.2 Grant Secret Access

```bash
PROJECT_ID="pacc-raw-data"
ACCOUNT="data-sync-custom@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant access to all secrets
for secret in base-vn-tokens mssql-connection worldfone-key; do
  gcloud secrets add-iam-policy-binding ${secret} \
    --member="serviceAccount:${ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
done

# Verify
gcloud secrets get-iam-policy base-vn-tokens
```

### 3.3 Test Secret Access

```bash
# Authenticate as service account
gcloud auth activate-service-account ${ACCOUNT} \
  --key-file=path/to/key.json

# Read secret
gcloud secrets versions access latest --secret="base-vn-tokens"
```

---

## 4. CLOUD RUN DEPLOYMENT

### 4.1 Build and Push Image

```bash
PROJECT_ID="pacc-raw-data"
IMAGE_NAME="data-sync-custom"
REGION="asia-southeast1"

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Create Artifact Registry repository (if not exists)
gcloud artifacts repositories create ${IMAGE_NAME} \
  --repository-format=docker \
  --location=${REGION}

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build image
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:latest .

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:latest
```

### 4.2 Deploy to Cloud Run

```bash
ACCOUNT="data-sync-custom@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud run deploy ${IMAGE_NAME} \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:latest \
  --platform=managed \
  --region=${REGION} \
  --no-allow-unauthenticated \
  --service-account=${ACCOUNT} \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --max-instances=10 \
  --min-instances=1 \
  --set-env-vars=GCP_PROJECT_ID=${PROJECT_ID},LOG_LEVEL=INFO \
  --ingress=internal

# Get service URL
SERVICE_URL=$(gcloud run services describe ${IMAGE_NAME} \
  --region=${REGION} \
  --format='value(status.url)')
echo "Service URL: ${SERVICE_URL}"
```

### 4.3 Configure VPC Access (Optional)

```bash
# If you need to access private MSSQL server
gcloud compute networks vpc-connectors create data-sync-custom-connector \
  --region=${REGION} \
  --subnet=default \
  --min-throughput=200 \
  --max-throughput=1000

# Update Cloud Run deployment to use VPC connector
gcloud run services update ${IMAGE_NAME} \
  --vpc-connector=data-sync-custom-connector \
  --region=${REGION}
```

---

## 5. CLOUD SCHEDULER SETUP

### 5.1 Create Scheduler Jobs

```bash
SERVICE_URL=$(gcloud run services describe data-sync-custom \
  --region=asia-southeast1 \
  --format='value(status.url)')
ACCOUNT="data-sync-custom@pacc-raw-data.iam.gserviceaccount.com"

# Base.vn sync daily at 2 AM UTC+7 (9 PM UTC)
gcloud scheduler jobs create http base-vn-sync \
  --location=asia-southeast1 \
  --schedule="0 21 * * *" \
  --http-method=POST \
  --uri="${SERVICE_URL}/sync/base-vn" \
  --oidc-service-account-email=${ACCOUNT} \
  --oidc-token-audience=${SERVICE_URL}

# MSSQL sync every 2 hours
gcloud scheduler jobs create http mssql-sync \
  --location=asia-southeast1 \
  --schedule="0 */2 * * *" \
  --http-method=POST \
  --uri="${SERVICE_URL}/sync/mssql" \
  --oidc-service-account-email=${ACCOUNT} \
  --oidc-token-audience=${SERVICE_URL}

# iPOS sync daily at 3 AM
gcloud scheduler jobs create http ipos-sync \
  --location=asia-southeast1 \
  --schedule="0 22 * * *" \
  --http-method=POST \
  --uri="${SERVICE_URL}/sync/ipos" \
  --oidc-service-account-email=${ACCOUNT} \
  --oidc-token-audience=${SERVICE_URL}

# WorldFone sync daily at 4 AM
gcloud scheduler jobs create http worldfone-sync \
  --location=asia-southeast1 \
  --schedule="0 23 * * *" \
  --http-method=POST \
  --uri="${SERVICE_URL}/sync/worldfone" \
  --oidc-service-account-email=${ACCOUNT} \
  --oidc-token-audience=${SERVICE_URL}
```

### 5.2 Test Scheduler

```bash
# Manually trigger a job (for testing)
gcloud scheduler jobs run base-vn-sync --location=asia-southeast1

# Check job execution
gcloud scheduler jobs describe base-vn-sync --location=asia-southeast1

# View job history
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=base-vn-sync" \
  --limit=10 \
  --format=json
```

---

## 6. MONITORING & LOGGING

### 6.1 View Logs

```bash
# Real-time logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=data-sync-custom" \
  --limit=50 \
  --format=json \
  --follow

# Specific error logs
gcloud logging read 'severity=ERROR AND resource.type=cloud_run_revision' \
  --limit=20 \
  --format=json

# By sync type
gcloud logging read '"sync_type":"base-vn"' \
  --limit=20 \
  --format=json
```

### 6.2 Create Metrics and Alerts

```bash
# Create log-based metric for failed syncs
gcloud logging metrics create sync_failures \
  --description="Count of failed sync operations" \
  --log-filter='severity=ERROR AND "sync" in textPayload'

# Create alert policy
gcloud alpha monitoring policies create \
  --display-name="Sync Failed Alert" \
  --condition-display-name="Failed Syncs" \
  --condition-expression='metric.type="logging.googleapis.com/user/sync_failures" AND resource.type="cloud_run_revision"' \
  --notification-channels=CHANNEL_ID
```

---

## 7. ENVIRONMENT VARIABLES REFERENCE

| Variable | Example | Required | Purpose |
|----------|---------|----------|---------|
| `GCP_PROJECT_ID` | pacc-raw-data | Yes | Google Cloud project ID |
| `LOG_LEVEL` | INFO | No | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `CLOUD_RUN` | true | Yes | Indicates running on Cloud Run |
| `PORT` | 8080 | Yes | HTTP port |
| `MSSQL_SALE_IP_ADDRESS` | server.net | Yes (if MSSQL) | MSSQL server address |
| `MSSQL_SALE_IP_USERNAME` | admin | Yes (if MSSQL) | MSSQL username |
| `MSSQL_SALE_IP_PASSWORD` | pass | Yes (if MSSQL) | MSSQL password |
| `DISABLE_AUTH` | false | No | Disable authentication (testing only) |

---

## 8. TROUBLESHOOTING

### Connection Issues to MSSQL

```bash
# Check ODBC driver installation in container
docker exec <container_id> odbcinst -j

# Test connectivity
docker exec <container_id> python -c "import pyodbc; print(pyodbc.drivers())"
```

### Secret Manager Access

```bash
# Test service account permissions
gcloud secrets versions access latest --secret="base-vn-tokens" \
  --impersonate-service-account=${ACCOUNT}
```

### Cloud Run Debug

```bash
# View detailed service logs
gcloud run services describe data-sync-custom --region=asia-southeast1

# Check service metrics
gcloud logging read "resource.type=cloud_run_revision AND metric.type=run.googleapis.com/request_count" \
  --format=json
```

---

## 9. CLEANUP

```bash
# Delete Cloud Run service
gcloud run services delete data-sync-custom --region=asia-southeast1

# Delete Scheduler jobs
gcloud scheduler jobs delete base-vn-sync --location=asia-southeast1

# Delete secrets
gcloud secrets delete base-vn-tokens
gcloud secrets delete mssql-connection
gcloud secrets delete worldfone-key

# Delete service account
gcloud iam service-accounts delete data-sync-custom@pacc-raw-data.iam.gserviceaccount.com
```

---

## 10. QUICK START CHECKLIST

- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed
- [ ] gcloud CLI installed and configured
- [ ] Service account created
- [ ] Secrets created in Secret Manager
- [ ] APIs enabled
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Scheduler jobs created
- [ ] Logs and alerts configured
