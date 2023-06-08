import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn_api,big_query

app='goal'
metric='cycle'
schema='BASEVN_GOAL'
table='cycle'

#execute
source_output=base_vn_api.get_cycles(app)
big_query.full_refresh_bq_insert_from_json(source_output,schema,table_id=table)
