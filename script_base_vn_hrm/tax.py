import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn

variable='tax'
schema='BASEVN_HRM'
job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("user_id",bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("percent",bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("eba",bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)
        ]
)

query_string='select max(last_update) as last_update from `pacc-raw-data.'+schema+'.'+variable+'`'

a=base_vn.while_loop_page_insert(app='hrm',
                                 schema=schema,
                                 column_name=variable,
                                 job_config=job_config_list,
                                 query_string_incre=query_string
                                 )

os.environ['RESULT'] = a