import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn

variable='interview'
component2='list'
schema='BASEVN_EHIRING'
#stop_words=['est_duration','candidate_export','followers','interacted','hr_set_cf']
stop_words=['date','est_duration','last_ping','followers','interacted','hr_set_cf']
job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)           
        ]
)

query_string='select max(last_update) as last_update from `pacc-raw-data.'+schema+'.'+variable+'_'+component2+'`'

a=base_vn.while_loop_page_insert(app='hiring',
                                 schema=schema,
                                 column_name=variable,
                                 job_config=job_config_list,
                                 query_string_incre=query_string,
                                 component2=component2,
                                 stop_words=stop_words
                                 )