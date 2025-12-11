# 📊 Data Sync Custom - Cloud Run Migration

> Triển khai hệ thống Data Sync từ Bash scripts sang Google Cloud Run

## 🚀 Quick Start

### For Decision Makers
- **Cost**: ~$10-15/month (vs $30-50 with EC2)
- **Scalability**: Automatic, unlimited
- **Maintenance**: Managed by Google Cloud
- **Time to Deploy**: 3 days
- **ROI**: Break-even in 2 months

👉 **Read**: `DEPLOYMENT_SUMMARY.md` (2 min read)

### For DevOps/Engineers
- **Architecture**: Serverless containers on Cloud Run
- **Orchestration**: Cloud Scheduler + HTTP endpoints
- **Credentials**: Google Secret Manager (not local files)
- **Logging**: Centralized JSON logs in Cloud Logging

👉 **Read**: `docs/deployment.md` (comprehensive guide)

### For Developers
- **Entry Point**: `main.py` (Flask HTTP server)
- **Handlers**: `handlers/` directory
- **Config**: `cloud_run_config/` for configuration
- **Code Refactoring**: `OPTIMIZATION_GUIDE.md` for tips

👉 **Read**: `docs/environment.md` (setup instructions)

---

## 📁 Project Structure

```
data-sync-custom/
│
├── 🆕 main.py                    # Flask HTTP server (Cloud Run entry point)
├── 🆕 Dockerfile                 # Container image definition
├── 🆕 cloudbuild.yaml            # CI/CD pipeline (GitHub → Cloud Run)
├── 🆕 requirements-cloud.txt      # Python dependencies
├── 🆕 .dockerignore              # Docker build filters
├── 🆕 .env.example               # Environment template
│
├── 🆕 cloud_run_config/          # Configuration & infrastructure
│   ├── __init__.py
│   ├── config.py                 # Config management + Secret Manager
│   ├── logger.py                 # JSON structured logging
│   └── error_handler.py          # Error handling & retry logic
│
├── 🆕 handlers/                  # Sync orchestration handlers
│   ├── __init__.py
│   ├── base_handler.py           # Abstract base class
│   ├── base_vn_handler.py        # Orchestrate Base.vn syncs
│   ├── mssql_handler.py          # Orchestrate MSSQL syncs
│   ├── ipos_handler.py           # Orchestrate iPOS syncs
│   └── worldfone_handler.py      # Orchestrate WorldFone syncs
│
├── 🆕 docs/                      # Documentation
│   ├── deployment.md             # Complete deployment guide
│   └── environment.md            # Environment setup
│
├── 🆕 DEPLOYMENT_SUMMARY.md      # Executive summary
├── 🆕 OPTIMIZATION_GUIDE.md      # Code optimization tips
│
├── ❌ bash_scheduling/           # DELETE (replaced by Cloud Scheduler)
├── ❌ credentials/               # DELETE (use Secret Manager)
├── ❌ sa.json                    # DELETE (use Workload Identity)
│
├── dbconnector/                  # KEEP (existing data connectors)
│   ├── base_vn.py
│   ├── base_vn_api.py
│   ├── big_query.py
│   ├── mssql.py
│   ├── ... (other connectors)
│
├── script_base_vn_*/             # KEEP (existing sync scripts)
├── script_mssql_*/               # KEEP (existing sync scripts)
├── script_ipos_*/                # KEEP (existing sync scripts)
│
├── README.md                     # THIS FILE
└── requirements.txt              # KEEP (existing requirements)
```

---

## 🔄 Before & After

### Before (Current Setup)
```
┌─────────────────────┐
│  Local Server/VM    │
│  (24/7 running)     │
│                     │
│ cron jobs ──────┐   │
│ bash scripts    │   │
│ python runners  │   │
└─────────────────────┘
         │
         ▼
  External APIs
  + Databases
  + BigQuery
```

**Issues:**
- ❌ Server runs 24/7 (expensive)
- ❌ No auto-scaling
- ❌ Hard-coded credentials in YAML
- ❌ Manual monitoring & alerts
- ❌ Limited error recovery

### After (Cloud Run)
```
┌──────────────────────────┐
│  Cloud Scheduler         │
│  (Trigger HTTP requests) │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│  Google Cloud Run        │
│  (Serverless Container)  │
│  - Auto-scales          │
│  - Pay-per-request      │
│  - Secure credentials   │
└───────────┬──────────────┘
            │
            ▼
  External APIs + Databases
```

**Benefits:**
- ✅ Auto-scaling
- ✅ Pay only for execution time
- ✅ Secure Secret Manager
- ✅ Centralized JSON logging
- ✅ Built-in monitoring
- ✅ 65% cost reduction

---

## 📚 Documentation Map

### Quick References
| Document | Duration | Audience |
|----------|----------|----------|
| `DEPLOYMENT_SUMMARY.md` | 2 min | Decision makers |
| `docs/deployment.md` | 20 min | DevOps/Architects |
| `docs/environment.md` | 30 min | Engineers/Implementers |
| `OPTIMIZATION_GUIDE.md` | 15 min | Developers |

### Step-by-Step Guides
1. **Planning**: See `DEPLOYMENT_SUMMARY.md`
2. **Setup**: See `docs/environment.md`
3. **Deployment**: See `docs/deployment.md`
4. **Code Changes**: See `OPTIMIZATION_GUIDE.md`

---

## 🔧 Key Components

### 1. main.py (Flask HTTP Server)
Handles incoming requests from Cloud Scheduler and routes to appropriate handlers.

**Endpoints:**
```
POST /sync/base-vn      - Sync Base.vn data
POST /sync/mssql        - Sync MSSQL data
POST /sync/ipos         - Sync iPOS CRM data
POST /sync/worldfone    - Sync WorldFone data
POST /sync/all          - Sync all data sources
GET  /health            - Health check
```

### 2. Handlers (handlers/*.py)
Orchestrate sync operations by dynamically running existing Python scripts.

**Design:**
- No modification needed to existing `script_*/` files
- Handlers import scripts dynamically
- Centralized error handling & logging
- Retry logic for resilience

### 3. Configuration (cloud_run_config/)
- `config.py`: Loads config from environment + Secret Manager
- `logger.py`: JSON structured logging for Cloud Logging
- `error_handler.py`: Error handling & retry strategy

### 4. Dockerfile
Builds container image with:
- Python 3.11
- ODBC Driver for SQL Server (pyodbc support)
- All dependencies from requirements-cloud.txt

### 5. CI/CD (cloudbuild.yaml)
Automated deployment pipeline:
- GitHub push → Cloud Build
- Build Docker image
- Push to Container Registry
- Deploy to Cloud Run

---

## 🚀 Deployment Timeline

```
Day 1: Preparation
├── Review new files
├── Local Docker testing
└── Prepare documentation

Day 2: GCP Setup
├── Create GCP resources
├── Build container
├── Deploy to staging
└── Test all endpoints

Day 3: Production
├── Production deployment
├── Configure monitoring
├── Cutover from bash
└── Validate data
```

---

## 💰 Cost Analysis

### Monthly Costs (Estimated)

**Old Setup (24/7 EC2):**
```
- EC2 t2.medium: $20-30
- EBS storage: $2-5
- Data transfer: $5-10
- Monitoring: Included
─────────────────────
Total: $27-45/month
```

**New Setup (Cloud Run):**
```
- Cloud Run requests: $5-10
  (100 requests/day × 30 days)
- Secret Manager: $1-2
- Cloud Logging: $0.5
- BigQuery: Already paying
─────────────────────
Total: $7-13/month
```

**Savings: 65-70% cost reduction** 💰

---

## ⚙️ Technical Architecture

### Request Flow
```
1. Cloud Scheduler triggers HTTP POST
   └─> /sync/base-vn, /sync/mssql, etc

2. main.py receives request
   └─> Route to appropriate handler

3. Handler orchestrates sync
   └─> Load config from Secret Manager
   └─> Setup logging
   └─> Run sync scripts dynamically

4. Sync scripts execute
   └─> Query APIs/Databases
   └─> Process data
   └─> Load to BigQuery

5. Results returned as JSON
   └─> HTTP response with status
   └─> Logs stored in Cloud Logging
```

### Error Handling
```
- Retries with exponential backoff
- Detailed error messages in logs
- Alert triggers on repeated failures
- Automatic recovery strategies
```

### Logging
```
All logs formatted as JSON:
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Sync completed",
  "sync_type": "base_vn",
  "duration_seconds": 45,
  "records_processed": 1500
}
```

---

## 🔐 Security Improvements

### Credentials Management
```
BEFORE: Hard-coded in YAML files
├── credentials/base_vn_token.yml
├── credentials/worldfone_key.yml
└── sa.json in git history

AFTER: Google Secret Manager
├── Encrypted at rest
├── Encrypted in transit
├── Access audited via Cloud Audit Logs
├── Automatic rotation support
└── No credentials in code/git
```

### Access Control
```
BEFORE: File permissions

AFTER: IAM roles + RBAC
├── Service account with minimal permissions
├── Separate secrets for each component
├── Audit trail of all access
└── Integration with Cloud Identity
```

---

## 📊 Monitoring & Alerts

### Built-in Metrics
- Request count & error rate
- Latency & performance
- Resource usage (CPU, Memory)
- Cold starts (if any)

### Alert Examples
```yaml
- Sync fails 3+ times in a row
- Request latency > 5 minutes
- Error rate > 5%
- BigQuery quota exceeded
```

---

## 🆘 Troubleshooting

### Common Issues

**"Secret not found"**
- Verify secret exists: `gcloud secrets list`
- Check permissions: `gcloud secrets get-iam-policy <secret>`

**"MSSQL connection timeout"**
- Verify network connectivity
- Check VPC connector configuration
- Review MSSQL firewall rules

**"BigQuery quota exceeded"**
- Check usage: `bq ls --project_id=<project>`
- Request quota increase in GCP Console

See `docs/environment.md` for complete troubleshooting guide.

---

## 📞 Support & Resources

### Documentation
- **Architecture**: `docs/deployment.md`
- **Setup**: `docs/environment.md`
- **Optimization**: `OPTIMIZATION_GUIDE.md`

### External Resources
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)

### Getting Help
- Check documentation first
- Review error logs in Cloud Logging
- Contact DevOps team

---

## ✅ Implementation Checklist

### Preparation
- [ ] Read all documentation
- [ ] Approve architecture
- [ ] Plan cutover strategy

### Development
- [ ] Review new files
- [ ] Test Docker image locally
- [ ] Verify all endpoints work

### GCP Setup
- [ ] Create service account
- [ ] Setup secrets in Secret Manager
- [ ] Enable required APIs
- [ ] Configure IAM permissions

### Deployment
- [ ] Build & push Docker image
- [ ] Deploy to staging
- [ ] Run integration tests
- [ ] Deploy to production
- [ ] Configure monitoring & alerts

### Cutover
- [ ] Run both systems in parallel
- [ ] Verify data integrity
- [ ] Monitor for issues
- [ ] Decommission old scripts

---

## 📈 Success Metrics

### Performance
- ✅ All syncs complete within SLA
- ✅ <5% error rate
- ✅ Response time <5 minutes

### Cost
- ✅ 65% cost reduction achieved
- ✅ Predictable monthly costs

### Reliability
- ✅ 99.9% uptime
- ✅ Automatic error recovery
- ✅ Comprehensive audit logs

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 15, 2024 | Initial deployment plan |

---

## 🎯 Next Steps

1. **Review** this README
2. **Read** `DEPLOYMENT_SUMMARY.md`
3. **Approve** the architecture
4. **Follow** `docs/environment.md` for setup
5. **Execute** `docs/deployment.md` for implementation

---

**Status**: ✅ Ready for implementation  
**Timeline**: 3 days  
**Owner**: DevOps Team  
**Contact**: [Your Email]
