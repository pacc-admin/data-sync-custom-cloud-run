import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn_api,big_query,dict_function
import json

app='goal'
schema='dbo'
table='goal'
column_updated='last_update'

#execute
raw_output=base_vn_api.get_base_goal_api(app)
source_output=dict_function.incremental_dict(raw_output,column_updated,schema,table)
big_query.bq_insert_from_json(source_output,schema,table_id=table)