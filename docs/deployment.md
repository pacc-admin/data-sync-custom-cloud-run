# PHƯƠNG ÁN TRIỂN KHAI TRÊN GOOGLE CLOUD RUN

## 1. TỔNG QUAN CẤU TRÚC

### Trước (Local/Bash)
```
bash_scheduling/
  ├── base_vn_run.sh
  ├── mssql_sale_run.sh
  ├── ipos_crm_run.sh
  └── run_worldfone.sh

credentials/
  ├── base_vn_token.yml      # Hard-coded tokens
  └── worldfone_key.yml

Main: Chạy bash scripts theo schedule cron
```

### Sau (Cloud Run)
```
main.py                        # Flask HTTP server
├── /sync/base-vn            # HTTP endpoint
├── /sync/mssql              # HTTP endpoint
├── /sync/ipos               # HTTP endpoint
├── /sync/worldfone          # HTTP endpoint
└── /sync/all                # Run all syncs

Cloud Scheduler -> HTTP request -> Cloud Run service
                                 ↓
                        Execute handlers
                                 ↓
                        Return JSON result
```

---

## 2. CÁC FILE CẦN THÊM

### A. Cấu hình & Orchestration

| File | Mục đích |
|------|---------|
| `main.py` | Flask entry point, HTTP endpoints |
| `Dockerfile` | Container image definition |
| `cloudbuild.yaml` | CI/CD pipeline (GitHub → Cloud Run) |
| `.dockerignore` | Ignore files khi build Docker |
| `.env.example` | Template biến môi trường |
| `requirements-cloud.txt` | Dependencies cho Cloud Run |

### B. Cloud Run Config

| File | Mục đích |
|------|---------|
| `cloud_run_config/config.py` | Quản lý config & Secret Manager |
| `cloud_run_config/logger.py` | Centralized logging (JSON format) |
| `cloud_run_config/error_handler.py` | Error handling & retry logic |

### C. Handlers (Orchestration)

| File | Mục đích |
|------|---------|
| `handlers/base_handler.py` | Abstract base class |
| `handlers/base_vn_handler.py` | Orchestrate Base.vn syncs |
| `handlers/mssql_handler.py` | Orchestrate MSSQL syncs |
| `handlers/ipos_handler.py` | Orchestrate iPOS syncs |
| `handlers/worldfone_handler.py` | Orchestrate WorldFone syncs |

### D. Documentation

| File | Mục đích |
|------|---------|
| `docs/deployment.md` | Hướng dẫn triển khai |
| `docs/environment.md` | Thiết lập môi trường |

---

## 3. CÁC FILE CẦN XÓA / REFACTOR

### A. Xóa (Bash scripts không cần thiết)

```bash
bash_scheduling/base_vn_run.sh
bash_scheduling/daily_task.sh
bash_scheduling/get_started.sh
bash_scheduling/google_sheet.sh
bash_scheduling/ipos_crm_run.sh
bash_scheduling/monthly_cleanup.sh
bash_scheduling/mssql_sale_run.sh
bash_scheduling/run_worldfone.sh
```

**Lý do:** Thay thế bằng HTTP endpoints + Cloud Scheduler

### B. Refactor (Xóa hard-coded credentials)

```
credentials/base_vn_token.yml  → Google Secret Manager
credentials/worldfone_key.yml  → Google Secret Manager
sa.json                        → Workload Identity + Service Account
```

---

## 4. TỐI ƯU CODE HIỆN TẠI

### A. dbconnector/yml_extract.py - CẦN REFACTOR

**Vấn đề:**
```python
# Hiện tại: đọc file YAML từ disk (không hoạt động trên Cloud Run)
def etract_variable_yml_dict(dictionary,file_name='base_vn_token'):
    a_yaml_file = open("credentials/"+file_name+".yml")  # ❌ Hardcoded path
```

**Giải pháp:**
```python
# Sau: đọc từ Secret Manager
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("GCP_PROJECT_ID")
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

### B. dbconnector/mssql.py - IMPROVEMENTS

**Thêm connection pooling:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'mssql+pyodbc://...',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

**Thêm timeout handling:**
```python
def mssql_query_pd(query_string, timeout=300):
    try:
        df = pd.read_sql(query, conn, timeout=timeout)
    except TimeoutError:
        logger.error("Query timeout")
        # Retry logic
```

### C. dbconnector/big_query.py - IMPROVEMENTS

**Thêm batch processing:**
```python
def bq_insert_batch(schema, table_id, dataframe, batch_size=1000):
    """Insert data in batches to avoid timeout."""
    total_rows = len(dataframe)
    for i in range(0, total_rows, batch_size):
        batch = dataframe.iloc[i:i+batch_size]
        bq_insert(schema, table_id, batch)
```

**Thêm error tracking:**
```python
def bq_insert(schema, table_id, dataframe):
    try:
        job = client.load_table_from_dataframe(...)
        job.result(timeout=300)
    except BadRequest as e:
        logger.error(f"BQ Error: {e.errors}")
        raise
```

### D. Script files - THÊM ERROR HANDLING

**Trước:**
```python
a=base_vn.single_page_insert(app, schema, table=component1, ...)
```

**Sau:**
```python
try:
    a = base_vn.single_page_insert(app, schema, table=component1, ...)
    logger.info(f"Sync completed: {component1}")
except Exception as e:
    logger.error(f"Sync failed: {component1}", exc_info=True)
    raise
```

---

## 5. DEPLOY STEPS

### Step 1: Prepare Repository

```bash
# Clone repo
git clone https://github.com/pacc-admin/data-sync-custom.git
cd data-sync-custom

# Add new files
git add Dockerfile main.py requirements-cloud.txt ...
git commit -m "Cloud Run deployment"
git push origin main
```

### Step 2: Setup Google Cloud

```bash
# Set project
gcloud config set project pacc-raw-data

# Create service account
gcloud iam service-accounts create data-sync-custom \
  --display-name="Data Sync Custom Service"

# Grant permissions
gcloud projects add-iam-policy-binding pacc-raw-data \
  --member=serviceAccount:data-sync-custom@pacc-raw-data.iam.gserviceaccount.com \
  --role=roles/bigquery.dataEditor

gcloud projects add-iam-policy-binding pacc-raw-data \
  --member=serviceAccount:data-sync-custom@pacc-raw-data.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Step 3: Create Secrets in Secret Manager

```bash
# Base.vn tokens
gcloud secrets create base-vn-token --data-file=- << EOF
{
  "hrm": "7383-...",
  "payroll": "7383-...",
  ...
}
EOF

# MSSQL credentials
gcloud secrets create mssql-connection --data-file=- << EOF
{
  "server": "your-server",
  "username": "your-user",
  "password": "your-pass"
}
EOF

# WorldFone key
gcloud secrets create worldfone-key --data-file=- << EOF
your-api-key
EOF
```

### Step 4: Setup Cloud Run

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Deploy
gcloud run deploy data-sync-custom \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --no-allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --service-account data-sync-custom@pacc-raw-data.iam.gserviceaccount.com
```

### Step 5: Setup Cloud Scheduler

```bash
# Enable Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# Create daily job (Base.vn sync at 2 AM)
gcloud scheduler jobs create http base-vn-sync \
  --location=asia-southeast1 \
  --schedule="0 2 * * *" \
  --http-method=POST \
  --uri="https://data-sync-custom-xxxxx.run.app/sync/base-vn" \
  --oidc-service-account-email=data-sync-custom@pacc-raw-data.iam.gserviceaccount.com

# Create hourly job (MSSQL sync every hour)
gcloud scheduler jobs create http mssql-sync \
  --location=asia-southeast1 \
  --schedule="0 * * * *" \
  --http-method=POST \
  --uri="https://data-sync-custom-xxxxx.run.app/sync/mssql" \
  --oidc-service-account-email=data-sync-custom@pacc-raw-data.iam.gserviceaccount.com
```

---

## 6. MONITORING & LOGGING

### Cloud Logging

Tất cả logs được ghi thành JSON format:
```
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "handlers.base_vn_handler",
  "message": "Starting sync",
  "sync_type": "account",
  "handler": "BaseVNHandler"
}
```

### View logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=data-sync-custom" \
  --limit 50 \
  --format json
```

### Setup alerts

```bash
# Create metric for failed syncs
gcloud monitoring metrics-descriptors create \
  custom.googleapis.com/sync_failures \
  --display-name="Sync Failures"

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --alert-strategy='[{"threshold_value": 1}]'
```

---

## 7. COST ESTIMATION

| Item | Chi phí/tháng |
|------|---------------|
| Cloud Run (2GB, 2 CPU, 300s/request × 100 requests/day) | ~$5-10 |
| Cloud Scheduler (10 jobs × 30 invocations/job) | ~$0.10 |
| Secret Manager (10 secrets, read usage) | ~$1 |
| Cloud Logging | ~$0.50 |
| **Total** | **~$10/tháng** |

*(So sánh: Server EC2 24/7 = ~$30-50/tháng)*

---

## 8. TIMELINE

| Giai đoạn | Thời gian | Công việc |
|----------|---------|----------|
| 1. Preparation | 1 ngày | Code review, unit tests |
| 2. Staging | 1 ngày | Deploy to staging Cloud Run, test |
| 3. Migration | 0.5 ngày | Verify data, cutover |
| 4. Production | 0.5 ngày | Monitor, optimize |
| **Total** | **3 ngày** | - |

---

## 9. ROLLBACK PLAN

```bash
# Giữ lại version cũ trong Bash scheduling
# Nếu cần rollback, chỉ cần disable Cloud Scheduler jobs
gcloud scheduler jobs pause base-vn-sync
gcloud scheduler jobs pause mssql-sync

# Và chạy bash scripts thủ công
./bash_scheduling/base_vn_run.sh
```

---

## 10. NEXT STEPS

1. ✅ Create Dockerfile + main.py
2. ✅ Setup handlers + config
3. ⏳ Test locally with Docker
4. ⏳ Setup GCP infrastructure
5. ⏳ Deploy to Cloud Run
6. ⏳ Configure Cloud Scheduler
7. ⏳ Monitor & optimize
8. ⏳ Decommission bash scripts
