import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn_api,big_query,dict_function
import json

app='goal'
schema='BASEVN_GOAL'
table='goal'
column_updated='last_update'
unique_key='id'

#execute
raw_output=base_vn_api.get_base_goal_api(app)
source_output=dict_function.incremental_dict(raw_output,column_updated,schema,table)
big_query.full_refresh_bq_insert_from_json(source_output,schema,table_id=table)


#job_config_list = bigquery.LoadJobConfig(
#        schema=[
#            bigquery.SchemaField("files",bigquery.enums.SqlTypeNames.RECORD, mode='REPEATED',
#                fields=(
#                    bigquery.SchemaField('rows', 'INTEGER'),
#                    bigquery.SchemaField('download','STRING'),
#                    bigquery.SchemaField('url','STRING'),
#                    bigquery.SchemaField('origin','INTEGER'),
#                    bigquery.SchemaField('is_templated','INTEGER'),
#                    bigquery.SchemaField('since','INTEGER'),
#                    bigquery.SchemaField('username','STRING'),
#                    bigquery.SchemaField('image','INTEGER'),
#                    bigquery.SchemaField('size','INTEGER'),
#                    bigquery.SchemaField('src','STRING'),
#                    bigquery.SchemaField('dimension','STRING'),
#                    bigquery.SchemaField('type','STRING'),
#                    bigquery.SchemaField('fid','STRING'),
#                    bigquery.SchemaField('id','STRING '),
#                    bigquery.SchemaField('name','STRING')
#                )
#            )            
#        ]
#)
