import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn

app='account'
component1='units'
table='groups'
schema='BASEVN_ACCOUNT'
stop_words=['num_people','type','has_image','status','official']

job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)
        ]
)

query_string_incre='select max(last_update) as last_update from `pacc-raw-data.'+schema+'.'+app+'`'

a=base_vn.single_page_insert(app,
                       schema,
                       table=table,
                       query_string_incre=query_string_incre,
                       component1=component1,
                       stop_words=stop_words,
                       job_config=job_config_list
                    )
