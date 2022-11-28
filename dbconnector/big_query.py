
from google.cloud import bigquery
import os

#Setting BQ credential in environment
os.environ.setdefault("GCLOUD_PROJECT", 'pacc-raw-data')
service_account_file_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

def connect_to_bq():
    client = bigquery.Client.from_service_account_json(service_account_file_path)
    return client

def bq_delete(client,schema,table_id):
    query = 'Delete from `pacc-raw-data.'+schema+'.'+table_id+'` where true'
    query_job = client.query(query)
    results = query_job.result()
    print(results)

def bq_insert(client,schema,table_id,dataframe):
    table_id = 'pacc-raw-data.'+schema+'.'+table_id
    job_config = bigquery.LoadJobConfig()
    job_config._properties['load']['schemaUpdateOptions'] = ['ALLOW_FIELD_ADDITION']

    job = client.load_table_from_dataframe(
        dataframe, table_id, job_config=job_config
    )
    job.result()
    
    table =  client.get_table(table_id)
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )