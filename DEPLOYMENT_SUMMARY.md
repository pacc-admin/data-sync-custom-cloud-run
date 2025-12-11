# 📊 CLOUD RUN DEPLOYMENT SUMMARY

## 🎯 OVERVIEW

Phương án triển khai hệ thống Data Sync từ local bash scripts sang **Google Cloud Run** - serverless container platform.

**Lợi ích:**
- ✅ Tự động scale theo tải
- ✅ Chi phí thấp (~$10-15/tháng vs $30-50 với EC2)
- ✅ Centralized logging & monitoring
- ✅ Secure credentials via Secret Manager
- ✅ Integrated with Cloud Scheduler
- ✅ Pay-per-request (không phải trả 24/7)

---

## 📁 CẤU TRÚC THAY ĐỔI

### ❌ CẦN XÓA (8 files)

```
bash_scheduling/
  ├── base_vn_run.sh              → Replaced by HTTP endpoint
  ├── daily_task.sh               → Replaced by Cloud Scheduler
  ├── get_started.sh              → Documentation only
  ├── google_sheet.sh             → Replaced by handler
  ├── ipos_crm_run.sh             → Replaced by handler
  ├── monthly_cleanup.sh          → Replaced by Cloud Scheduler
  ├── mssql_sale_run.sh           → Replaced by handler
  └── run_worldfone.sh            → Replaced by handler

credentials/
  ├── base_vn_token.yml           → Secret Manager
  └── worldfone_key.yml           → Secret Manager

❌ sa.json                          → Workload Identity / IAM
```

### ✅ CẦN THÊM (20+ files)

#### Core Files (7)
```
main.py                            # Flask HTTP server
Dockerfile                         # Container image
cloudbuild.yaml                    # CI/CD pipeline
requirements-cloud.txt             # Dependencies
.dockerignore                      # Docker build filters
.env.example                       # Environment template
OPTIMIZATION_GUIDE.md              # Code optimization tips
```

#### Cloud Config (4)
```
cloud_run_config/
  ├── __init__.py
  ├── config.py                   # Configuration management
  ├── logger.py                   # JSON logging
  └── error_handler.py            # Error handling & retry
```

#### Handlers (5)
```
handlers/
  ├── __init__.py
  ├── base_handler.py             # Abstract base
  ├── base_vn_handler.py          # Base.vn sync orchestration
  ├── mssql_handler.py            # MSSQL sync orchestration
  ├── ipos_handler.py             # iPOS sync orchestration
  └── worldfone_handler.py        # WorldFone sync orchestration
```

#### Documentation (2+)
```
docs/
  ├── deployment.md               # Complete deployment guide
  └── environment.md              # Environment setup steps
```

---

## 🔄 FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                     CLOUD SCHEDULER                          │
│  (Triggers HTTP requests on schedule)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           GOOGLE CLOUD RUN                                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ main.py (Flask)                                      │   │
│  │  - /sync/base-vn                                     │   │
│  │  - /sync/mssql                                       │   │
│  │  - /sync/ipos                                        │   │
│  │  - /sync/worldfone                                   │   │
│  │  - /sync/all                                         │   │
│  │  - /health                                           │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Handlers (Orchestration Layer)                       │   │
│  │  - BaseVNHandler                                     │   │
│  │  - MSSQLHandler                                      │   │
│  │  - iPOSHandler                                       │   │
│  │  - WorldFoneHandler                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Legacy Script Runners (dbconnector)                  │   │
│  │  - Import existing script_*/ files dynamically       │   │
│  │  - No modification needed to existing scripts        │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ External Services                                    │   │
│  │  - BigQuery (INSERT/DELETE operations)              │   │
│  │  - MSSQL Server (Query via pyodbc)                  │   │
│  │  - Base.vn API (HTTP requests)                      │   │
│  │  - WorldFone API (HTTP requests)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  BigQuery    │    │ Secret Mgr   │    │Cloud Logging │
    │  (data lake) │    │ (credentials)│    │  (JSON logs) │
    └──────────────┘    └──────────────┘    └──────────────┘
```

---

## 🚀 DEPLOYMENT STEPS (3 ngày)

### Day 1: Preparation (8 hours)
```
[ ] Code review & finalize new files
[ ] Setup local Docker environment
[ ] Test main.py locally
[ ] Prepare documentation
```

### Day 2: GCP Setup & Testing (8 hours)
```
[ ] Create GCP resources (service account, secrets, etc)
[ ] Build & test Docker image
[ ] Deploy to staging Cloud Run
[ ] Test all endpoints
[ ] Configure Cloud Scheduler (staging)
```

### Day 3: Production Deployment (8 hours)
```
[ ] Production deployment
[ ] Configure monitoring & alerts
[ ] Cutover from bash scripts
[ ] Verify data integrity
[ ] Setup rollback plan
```

---

## 📊 COST COMPARISON

| Item | Local EC2 24/7 | Cloud Run (pay-per-use) |
|------|-------------|----------------------|
| Compute | $15-30/mo | $5-10/mo |
| Storage | $2-5/mo | $2-3/mo |
| Database | $10-20/mo | Included (BQ) |
| Monitoring | Included | $0.5/mo |
| **Total** | **$30-55/mo** | **$10-15/mo** |

**Savings: ~65% cost reduction** 💰

---

## 🔧 CODE OPTIMIZATIONS

### 1. yml_extract.py Refactor
```python
# Before: Read from local YAML file
def etract_variable_yml_dict(dictionary, file_name='base_vn_token'):
    a_yaml_file = open("credentials/"+file_name+".yml")  # ❌ Local file

# After: Read from Secret Manager
from google.cloud import secretmanager
def get_secret(secret_id: str) -> dict:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return json.loads(response.payload.data)
```

### 2. mssql.py Improvements
```python
# Add: Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(..., poolclass=QueuePool, pool_size=10)

# Add: Timeout handling & retry
def mssql_query_pd(query, timeout=300, max_retries=3):
    for attempt in range(max_retries):
        try:
            return pd.read_sql(query, engine, timeout=timeout)
        except TimeoutError:
            time.sleep(2 ** attempt)
```

### 3. big_query.py Improvements
```python
# Add: Batch processing for large datasets
def bq_insert_batch(schema, table, df, batch_size=1000):
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        bq_insert(schema, table, batch)  # Retry-safe

# Add: Better error messages
except BadRequest as e:
    logger.error(f"BQ Schema Error: {e.errors}")
    raise
```

### 4. New Structured Logging
```python
# All logs as JSON for Cloud Logging
logger.info("Sync completed", extra={
    "sync_type": "base_vn",
    "records_processed": 1500,
    "duration_seconds": 45
})

# Output:
# {
#   "timestamp": "2024-01-15T10:30:00Z",
#   "level": "INFO",
#   "message": "Sync completed",
#   "sync_type": "base_vn",
#   "records_processed": 1500,
#   "duration_seconds": 45
# }
```

---

## 🔐 SECURITY IMPROVEMENTS

| Aspect | Before | After |
|--------|--------|-------|
| Credentials | Local YAML files | Google Secret Manager |
| Access Control | File permissions | IAM roles + RBAC |
| Secrets in Logs | ⚠️ Possible | ✅ Redacted |
| Audit Trail | ❌ None | ✅ Cloud Audit Logs |
| Encryption | ❌ Unencrypted | ✅ Encrypted in transit & at rest |

---

## 📈 MONITORING & ALERTS

### Metrics Collected
```
- Request count & latency
- Error rates by sync type
- Data rows processed
- Execution duration
- Memory usage
- Cold starts (if any)
```

### Alert Triggers
```
- Sync failed (error rate > 5%)
- Timeout (execution > 1 hour)
- Invalid data (schema mismatch)
- MSSQL connection error
- BigQuery quota exceeded
```

---

## ✅ CHECKLIST - FILE ADDITIONS

```
Core Files
[ ] main.py
[ ] Dockerfile
[ ] cloudbuild.yaml
[ ] requirements-cloud.txt
[ ] .dockerignore
[ ] .env.example

Cloud Config
[ ] cloud_run_config/__init__.py
[ ] cloud_run_config/config.py
[ ] cloud_run_config/logger.py
[ ] cloud_run_config/error_handler.py

Handlers
[ ] handlers/__init__.py
[ ] handlers/base_handler.py
[ ] handlers/base_vn_handler.py
[ ] handlers/mssql_handler.py
[ ] handlers/ipos_handler.py
[ ] handlers/worldfone_handler.py

Documentation
[ ] docs/deployment.md
[ ] docs/environment.md
[ ] OPTIMIZATION_GUIDE.md
```

---

## 📋 FILES TO DELETE (Cleanup)

```bash
# Bash scripts (no longer needed)
rm -rf bash_scheduling/*.sh

# Local credentials (moved to Secret Manager)
rm -f credentials/*.yml

# Service account key file (use Workload Identity instead)
rm -f sa.json
```

**Note:** Keep them in git history with `.gitignore` update

---

## 🎓 NEXT ACTIONS

1. **Review & Approve**
   - Review all new files
   - Verify architecture aligns with requirements
   - Approve optimization strategy

2. **Prepare GCP Environment**
   - Create GCP project/resources
   - Setup service accounts & IAM
   - Configure secrets

3. **Local Testing**
   - Build Docker image
   - Test main.py endpoints
   - Verify handler logic

4. **Cloud Deployment**
   - Setup CI/CD pipeline
   - Deploy to staging
   - Deploy to production

5. **Cutover & Validation**
   - Run both systems in parallel
   - Verify data integrity
   - Monitor for issues

---

## 📞 SUPPORT

For questions about:
- **Architecture**: See `docs/deployment.md`
- **Setup**: See `docs/environment.md`
- **Code changes**: See `OPTIMIZATION_GUIDE.md`
- **Troubleshooting**: See individual handler files

---

**Status**: ✅ Ready for implementation
**Estimated Timeline**: 3 days
**Cost Savings**: ~65% reduction
**Scalability**: ✅ Unlimited with Cloud Run
