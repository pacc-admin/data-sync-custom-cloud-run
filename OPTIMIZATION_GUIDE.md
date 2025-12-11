"""
OPTIMIZATION SUMMARY FOR CODE REFACTORING

This file documents recommended optimizations for existing code
to work properly with Google Cloud Run deployment.
"""

# ===== 1. REFACTOR: dbconnector/yml_extract.py =====
"""
BEFORE (Current - breaks on Cloud Run):
    def etract_variable_yml_dict(dictionary, file_name='base_vn_token'):
        a_yaml_file = open("credentials/"+file_name+".yml")  # ❌ Local file
        parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
        token = parsed_yaml_file[dictionary]
        return token

AFTER (Cloud Run compatible):
"""

from google.cloud import secretmanager
import json
import os

def get_base_vn_token(component: str) -> str:
    """Get Base.vn API token from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("GCP_PROJECT_ID")
    
    name = f"projects/{project_id}/secrets/base-vn-tokens/versions/latest"
    response = client.access_secret_version(request={"name": name})
    
    secrets = json.loads(response.payload.data.decode("UTF-8"))
    return secrets.get(component)

def get_secret(secret_name: str) -> str:
    """Generic secret retrieval from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("GCP_PROJECT_ID")
    
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


# ===== 2. REFACTOR: dbconnector/mssql.py =====
"""
IMPROVEMENTS:
- Add connection pooling
- Add timeout handling
- Add retry logic
- Add logging
"""

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import logging
from datetime import date, timedelta
import time

logger = logging.getLogger(__name__)

# Connection pooling
_engine = None

def get_mssql_engine():
    """Get or create MSSQL connection pool."""
    global _engine
    if _engine is not None:
        return _engine
    
    import os
    server = os.environ.get("MSSQL_SALE_IP_ADDRESS")
    username = os.environ.get("MSSQL_SALE_IP_USERNAME")
    password = os.environ.get("MSSQL_SALE_IP_PASSWORD")
    
    connection_string = f'mssql+pyodbc://{username}:{password}@{server}:1433/master?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes'
    
    _engine = create_engine(
        connection_string,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        echo=False
    )
    return _engine

def mssql_query_pd(query_string, timeout=300, max_retries=3):
    """Query MSSQL with retry logic."""
    import pandas as pd
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Executing MSSQL query (attempt {attempt+1}/{max_retries})")
            engine = get_mssql_engine()
            df = pd.read_sql(query_string, engine, timeout=timeout)
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
        
        except TimeoutError as e:
            logger.warning(f"Query timeout (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Query failed after {max_retries} attempts")
                raise
        
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise

def mssql_query_pd_sale(query_string, timeout=300):
    """Query MSSQL Sale database with formatting."""
    import pandas as pd
    
    df = mssql_query_pd(query_string, timeout=timeout)
    
    # Convert date columns
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], format='%d/%m/%y')
        except Exception as e:
            logger.warning(f"Could not convert {col} to datetime: {e}")
    
    df['LOADED_DATE'] = pd.to_datetime('today', format='%Y-%m-%d %H:%M:%S.%f')
    logger.info(f"Data formatted, sample:\n{df.head(5)}")
    return df


# ===== 3. REFACTOR: dbconnector/big_query.py =====
"""
IMPROVEMENTS:
- Add batch processing
- Add better error handling
- Add progress tracking
- Add retry logic
"""

from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)

def bq_insert_batch(schema, table_id, dataframe, batch_size=1000, max_retries=3):
    """
    Insert data into BigQuery in batches to avoid timeout.
    
    Args:
        schema: BigQuery dataset name
        table_id: BigQuery table name
        dataframe: Pandas DataFrame to insert
        batch_size: Number of rows per batch
        max_retries: Max retry attempts
    """
    import pandas as pd
    
    total_rows = len(dataframe)
    table_id_full = f"pacc-raw-data.{schema}.{table_id}"
    
    logger.info(f"Inserting {total_rows} rows into {table_id_full} (batch_size={batch_size})")
    
    client = bigquery.Client()
    inserted = 0
    
    for i in range(0, total_rows, batch_size):
        batch = dataframe.iloc[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_rows + batch_size - 1) // batch_size
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.info(f"Inserting batch {batch_num}/{total_batches} ({len(batch)} rows)")
                
                job_config = bigquery.LoadJobConfig()
                job = client.load_table_from_dataframe(
                    batch,
                    table_id_full,
                    job_config=job_config
                )
                job.result(timeout=300)
                
                inserted += len(batch)
                logger.debug(f"Batch {batch_num} inserted successfully")
                break
            
            except Exception as e:
                logger.warning(f"Batch {batch_num} failed (attempt {retry_count+1}): {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Batch {batch_num} failed after {max_retries} attempts")
                    raise
                import time
                time.sleep(2 ** retry_count)
    
    logger.info(f"Successfully inserted {inserted}/{total_rows} rows")
    return inserted


# ===== 4. REFACTOR: dbconnector/base_vn_api.py =====
"""
IMPROVEMENTS:
- Add caching
- Add timeout handling
- Add rate limiting
"""

import requests
import logging
import time
from functools import lru_cache

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter to avoid API throttling."""
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait(self):
        """Wait if needed to respect rate limit."""
        now = time.time()
        # Remove old requests outside time window
        self.requests = [t for t in self.requests if now - t < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f}s")
                time.sleep(wait_time)
        
        self.requests.append(now)

_rate_limiter = RateLimiter()

def base_vn_connect_hiring(component1, app='hiring', component2='list', 
                           updated_from=0, page=0, para1='', value1='',
                           timeout=30, max_retries=3):
    """Connect to Base.vn hiring API with timeout and retry."""
    from yml_extract import get_base_vn_token
    
    for attempt in range(max_retries):
        try:
            _rate_limiter.wait()
            
            access_token = get_base_vn_token(app)
            h = {"Content-type": "application/x-www-form-urlencoded"}
            
            page_dict = {'page': page}
            updated_from_dict = {'updated_from': updated_from}
            
            if para1 == '':
                p = {**access_token, **updated_from_dict, **page_dict}
            else:
                p = {**access_token, **updated_from_dict, **page_dict, **{para1: value1}}
            
            url = f"https://{app}.base.vn/publicapi/v2/{component1}/{component2}"
            
            logger.debug(f"Requesting {url} (attempt {attempt+1})")
            response = requests.post(url, headers=h, data=p, timeout=timeout)
            response.raise_for_status()
            
            raw_output = response.json()
            logger.debug(f"Response received: {len(str(raw_output))} bytes")
            return raw_output
        
        except requests.exceptions.Timeout as e:
            logger.warning(f"Request timeout (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
        
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise


# ===== 5. ERROR HANDLING WRAPPER =====
"""
Add to each sync script for better error handling
"""

import logging
import traceback

logger = logging.getLogger(__name__)

def run_sync_with_error_handling(sync_function, sync_name: str):
    """Decorator for better error handling in sync scripts."""
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"Starting sync: {sync_name}")
            result = sync_function(*args, **kwargs)
            logger.info(f"Sync completed successfully: {sync_name}")
            return result
        
        except Exception as e:
            logger.error(f"Sync failed: {sync_name}", exc_info=True)
            # Send error to monitoring (optional)
            # alert_error(sync_name, str(e))
            raise
    
    return wrapper


# ===== 6. LOGGING SETUP FOR EACH SCRIPT =====
"""
Add to top of each script_*/xxx.py file:
"""

import logging
from cloud_run_config.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Then use: logger.info("message")
# This automatically formats as JSON for Cloud Logging


# ===== MIGRATION CHECKLIST =====
"""
[ ] Refactor yml_extract.py to use Secret Manager
[ ] Update mssql.py with connection pooling
[ ] Update big_query.py with batch processing
[ ] Update base_vn_api.py with rate limiting
[ ] Add error handling wrapper to each script
[ ] Add logging setup to each script
[ ] Test locally with Docker
[ ] Deploy to Cloud Run
[ ] Monitor logs and fix issues
"""
