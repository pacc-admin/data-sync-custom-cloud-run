import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn

app='goal'
schema='BASEVN_GOAL'
stop_words=['data',
            'starred',
            'liked',
            'stats',
            'computed_visibility',
            'acl'
        ]
job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)
        ]
)

query_string_incre='select max(last_update) as last_update from `pacc-raw-data.'+schema+'.'+app+'`'

a=base_vn.single_page_insert(app,
                       schema,
                       query_string_incre,
                       stop_words=stop_words,
                       job_config=job_config_list
                    )
