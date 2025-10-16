
from google.cloud import bigquery
import pandas_gbq
import pandas as pd
import numpy as np
from google.oauth2 import service_account
import os
import io
import json
import math

#Setting BQ credential in environment
os.environ.setdefault("GCLOUD_PROJECT", 'pacc-raw-data')
service_account_file_path=os.environ.get("PACC_SA_RAW")

def connect_to_bq():
    client = bigquery.Client.from_service_account_json(service_account_file_path)
    return client

def bq_delete(schema,table_id,condition=''):
    client=connect_to_bq()
    if condition=='':
        print('no columns is removed')
    else:
        query = 'Delete from `pacc-raw-data.'+schema+'.'+table_id+'` where '+condition
        query_job = client.query(query)
        results = query_job.result()
        print(results)

def bq_query(query_string):
    client=connect_to_bq()
    query_job = client.query(query=query_string)
    results = query_job.result()
    print(results)

def bq_insert(schema,table_id,dataframe,condition='',unique_key='',job_config=bigquery.LoadJobConfig()):
    client=connect_to_bq()
    table_id_full = 'pacc-raw-data.'+schema+'.'+table_id
    job_config = job_config
    job_config._properties['load']['schemaUpdateOptions'] = ['ALLOW_FIELD_ADDITION']

    if dataframe.to_dict('records')==[]:
        print('No Insert')
    else:
        print('continue')
        
        #deduplication
        if unique_key=='':
            print('No dedup')
        else:
            dataframe=dataframe.drop_duplicates(subset=unique_key)
            print('Dedup completed')
        
        # Try to coerce DataFrame columns to existing BigQuery table schema (if table exists)
        try:
            table = client.get_table(table_id_full)
            schema_map = {f.name: {'type': f.field_type.upper(), 'mode': f.mode} for f in table.schema}
            print('Existing table schema detected, coercing columns to match types and modes...')
            for col, meta in schema_map.items():
                if col not in dataframe.columns:
                    continue
                ftype = meta['type']
                fmode = (meta.get('mode') or '').upper()
                s = dataframe[col]
                try:
                    # Handle REPEATED (arrays) mode: ensure values are lists
                    if fmode == 'REPEATED':
                        def ensure_list(v):
                            if v is None or (isinstance(v, float) and pd.isna(v)):
                                return None
                            if isinstance(v, list):
                                return v
                            if isinstance(v, str):
                                # try parse JSON array
                                try:
                                    parsed = json.loads(v)
                                    if isinstance(parsed, list):
                                        return parsed
                                except Exception:
                                    pass
                                # fallback: split by comma if looks like CSV
                                if ',' in v:
                                    return [item.strip() for item in v.split(',') if item.strip()!='']
                                return [v]
                            # other scalars -> wrap
                            return [v]

                        dataframe[col] = s.map(ensure_list)
                        continue

                    # For non-repeated fields, coerce according to declared type
                    if ftype in ('STRING', 'BYTES'):
                        dataframe[col] = s.where(pd.notna(s), pd.NA).astype('string')
                    elif ftype in ('INTEGER', 'INT64'):
                        dataframe[col] = pd.to_numeric(s, errors='coerce').astype('Int64')
                    elif ftype in ('FLOAT', 'FLOAT64', 'NUMERIC', 'DECIMAL'):
                        dataframe[col] = pd.to_numeric(s, errors='coerce').astype('Float64')
                    elif ftype in ('BOOLEAN',):
                        dataframe[col] = s.map(lambda v: True if str(v).lower() in ('true','1','t','y') else (False if str(v).lower() in ('false','0','f','n') else pd.NA)).astype('boolean')
                    elif ftype in ('TIMESTAMP','DATETIME','DATE'):
                        dataframe[col] = pd.to_datetime(s, errors='coerce')
                    elif ftype == 'JSON':
                        dataframe[col] = s.map(lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v)
                except Exception as e:
                    print(f'Warning: coercion of column {col} to {ftype} (mode={fmode}) failed: {e}; leaving as-is')
        except Exception as e:
            # table may not exist or permission denied; continue with conservative normalization
            print('Could not fetch table schema (table may not exist) - will apply conservative normalization:', e)

        # attempt load via pandas->pyarrow
        try:
            job = client.load_table_from_dataframe(
                dataframe, table_id_full, job_config=job_config
            )
        except Exception as e:
            # fallback: if pyarrow conversion fails, try loading as NDJSON
            err_msg = str(e)
            print('load_table_from_dataframe failed:', err_msg)
            print('Falling back to newline-delimited JSON load (slower but tolerant).')

            try:
                job_config_json = bigquery.LoadJobConfig()
                job_config_json.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
                job_config_json.autodetect = True
                job_config_json._properties['load']['schemaUpdateOptions'] = ['ALLOW_FIELD_ADDITION']

                records = dataframe.where(pd.notna(dataframe), None).to_dict(orient='records')
                json_data = "\n".join([json.dumps(r, default=str) for r in records])
                json_file = io.StringIO(json_data)

                job = client.load_table_from_file(json_file, table_id_full, job_config=job_config_json)
            except Exception as e2:
                print('Fallback NDJSON load also failed:', str(e2))
                raise

        #remove column with id matches the inserted rows
        bq_delete(schema,table_id,condition=condition)
        job.result()
        table=client.get_table(table_id_full)
        print(str(
                "{} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        ))
    
    
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
          

def bq_latest_date(date_schema,schema,table_id,condition=''):
    #finding latest date from BQ table
    if condition=='':
        condition_parse = 'true'
    else:
        condition_parse = condition
    query_string='select max(cast('+date_schema+' as date)) as '+date_schema+' from `pacc-raw-data.'+schema+'.'+table_id+'`'+' where '+condition_parse
    print(query_string)
    df=bq_pandas(query_string)
    print(df)
    if df[date_schema].astype(str).to_list()[0]=='NaT':
        recent_loaded_date='1970-01-01'
    else:
        recent_loaded_date=df[date_schema].astype(str).to_list()[0]
    return recent_loaded_date

def append_tables(schema_to_append,schema_appended,table_id):
    query_string='''
        SELECT column_name FROM pacc-raw-data.'''+schema_to_append+'''.INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = '''+"'"+table_id+"'"

    #Get columns name    
    df=bq_pandas(query_string=query_string)
    column_lists=df['column_name'].astype(str).to_list()
    columns=",\n".join(column_lists)
    
    #Insert Query
    query_string='''
      insert into `pacc-raw-data.'''+schema_appended+'''.'''+table_id+'''` (
        '''+columns+'''
      )
    
    select
        '''+columns+'''
    from
      `pacc-raw-data.'''+schema_to_append+'''.'''+table_id+'''`
    '''
    print(query_string)
    
    #BQ insert
    bq_query(query_string)

def bq_insert_from_json(source_output,schema,table_id,job_config=bigquery.LoadJobConfig()):
    client=connect_to_bq()
    table_id_full = 'pacc-raw-data.'+schema+'.'+table_id
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.autodetect = True
    job_config._properties['load']['schemaUpdateOptions'] = ['ALLOW_FIELD_ADDITION']

    if source_output == []:
        print('stop')
    else:
        json_data = "\n".join([json.dumps(d) for d in source_output])
        json_file = io.StringIO(json_data)
    
        #load
        job = client.load_table_from_file(json_file, table_id_full, job_config=job_config)
    
        job.result()
        table=client.get_table(table_id_full)
        print(str(
                "{} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        ))

def incremental_bq_insert_from_json(source_output,schema,table_id,unique_key,job_config=bigquery.LoadJobConfig()):
    #condition to exclude
    try:
        condition='cast('+unique_key+' as string) in '+ '(' + ','.join([f"'{source_output_dict[unique_key]}'" for source_output_dict in source_output]) + ')'
    except:
        print('error occurs')
    
    bq_delete(schema,table_id,condition=condition)
    bq_insert_from_json(source_output,schema,table_id,job_config=job_config)

def full_refresh_bq_insert_from_json(source_output,schema,table_id,job_config=bigquery.LoadJobConfig()):
    #condition to exclude
    condition='true'
    
    bq_delete(schema,table_id,condition=condition)
    bq_insert_from_json(source_output,schema,table_id,job_config=job_config)

def bq_last_update(query_string_incre,column_updated):
    try:
        bq_table_date=bq_pandas(query_string_incre)[column_updated].astype(float).to_list()[0]
        
        if math.isnan(bq_table_date)==True:
            last_updated_date=0
        else:
            last_updated_date=bq_table_date
    except:
        last_updated_date=0
    
    return last_updated_date
#json convert
#print(goal_detail)
#json_data = "\n".join([json.dumps(d) for d in goal_detail])

def bq_insert_from_json2(source_output,schema,table_id,job_config):
    client=connect_to_bq()
    table_id_full = 'pacc-raw-data.'+schema+'.'+table_id
 
    if source_output == []:
        print('stop')
    else:

        #load
        job = client.load_table_from_json(source_output, table_id_full, job_config=job_config)
    
        job.result()
        table=client.get_table(table_id_full)
        print(str(
                "{} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        ))

def full_refresh_bq_insert_from_json2(source_output,schema,table_id,job_config):
    #condition to exclude
    condition='true'
    
    bq_delete(schema,table_id,condition=condition)
    bq_insert_from_json2(source_output,schema,table_id,job_config=job_config)
