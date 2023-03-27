
from google.cloud import bigquery
import pandas_gbq
from google.oauth2 import service_account
import os

#Setting BQ credential in environment
os.environ.setdefault("GCLOUD_PROJECT", 'pacc-raw-data')
service_account_file_path=os.environ.get("PACC_SA_RAW")

def connect_to_bq():
    client = bigquery.Client.from_service_account_json(service_account_file_path)
    return client

def bq_delete(schema,table_id,condition='true'):
    client=connect_to_bq()
    query = 'Delete from `pacc-raw-data.'+schema+'.'+table_id+'` where '+condition
    query_job = client.query(query)
    results = query_job.result()
    print(results)

def bq_query(query_string):
    client=connect_to_bq()
    query_job = client.query(query=query_string)
    results = query_job.result()
    print(results)

def bq_insert(schema,table_id,dataframe,job_config = bigquery.LoadJobConfig()):
    client=connect_to_bq()
    table_id = 'pacc-raw-data.'+schema+'.'+table_id
    job_config = job_config
    job_config._properties['load']['schemaUpdateOptions'] = ['ALLOW_FIELD_ADDITION']

    try:
        job = client.load_table_from_dataframe(
            dataframe, table_id, job_config=job_config
        )
        
        job.result()

        result='Success, data are loaded'
        #table =  client.get_table(table_id)
        #print(
        #    "Loaded {} rows and {} columns to {}".format(
        #        table.num_rows, len(table.schema), table_id
        #    )
        #)

    except:
        result='Failed, Please rerun and check'
        print(
            str(job = client.load_table_from_dataframe(
                dataframe, table_id, job_config=job_config
            ))
        )
    return result
    
def bq_pandas(query_string):
    credentials = service_account.Credentials.from_service_account_file(service_account_file_path)
    querry_bq=pandas_gbq.read_gbq(query_string, project_id="pacc-raw-data", credentials=credentials)
    return querry_bq

#BQ insert
def bq_insert_streaming(rows_to_insert,table_id,object):
    client=connect_to_bq()
    if rows_to_insert == []:
      print('stop')
    else:
      errors = client.insert_rows_json(table_id, rows_to_insert)   # Make an API request
      if errors == []:
          print("New rows have been added.")
      else:
          print("Encountered errors while inserting rows: {}".format(errors))
          f = open('script_ipos_crm/errors.txt', 'a')
          f.write(f"{object}\n")
          f.write(f"{errors}\n")
          f.close()
          print("data written")
          

def bq_latest_date(date_schema,schema,table_id):
    #finding latest date from BQ table
    df=bq_pandas(query_string='select max(cast('+date_schema+' as date)) as tran_date from `pacc-raw-data.'+schema+'.'+table_id+'`')
    recent_loaded_date=df[date_schema].astype(str).to_list()[0]
    return recent_loaded_date
