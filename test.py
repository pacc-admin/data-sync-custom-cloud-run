from google.cloud import bigquery
import os
os.environ.setdefault("GCLOUD_PROJECT", 'pacc-raw-data')
service_account_file_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

project_id = 'pacc-raw-data'
client = bigquery.Client.from_service_account_json(service_account_file_path)
table_id='pacc-raw-data.test1.test_bq'

rows_to_insert = [
    {"title": "this is ery"}
]

errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
if errors == []:
    print("New rows have been added.")
else:
    print("Encountered errors while inserting rows: {}".format(errors))








