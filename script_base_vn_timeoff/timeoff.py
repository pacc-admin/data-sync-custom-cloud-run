from google.cloud import bigquery
import sys,os
import json
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import json_schema_bq, big_query, base_vn_api

# Create a BigQuery client
client = bigquery.Client()

# Define the dataset ID and table ID
schema='BASEVN_TIMEOFF'
table='timeoff'
file_path = '/Users/namxuan97/Documents/vscode_space/pacc/pacc-data-sync-custom/metadata/basevn/timeoff/timeoff.json'

# Define the job configuration
job_config = bigquery.LoadJobConfig(
    schema=json_schema_bq.parse_json_schema_from_file(file_path),
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
)
job_config._properties['load']['schemaUpdateOptions'] = ['ALLOW_FIELD_ADDITION']

source_output = base_vn_api.get_base_timeoff()

#convert changable nested fields to string 
rows_to_insert = []
for row in source_output:
    row['data'] = str(row['data'])
    rows_to_insert.append(row)

#Load the data into BigQuery
big_query.full_refresh_bq_insert_from_json2(source_output,schema,table_id=table,job_config=job_config)
