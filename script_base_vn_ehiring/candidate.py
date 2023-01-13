import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn


#finding opening id
opening_raw=base_vn.base_vn_connect(app='hiring',component1='opening',component2='list')
opening=opening_raw['openings']
opening_ids=[sub['id'] for sub in opening]
#opening_ids=['892']

#specify other variables
variable='candidate'
component2='list'
schema='BASEVN_EHIRING'
job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)            
        ]
)

for opening_id in opening_ids:
    print(opening_id)
    query_string='''
                    select max(last_update) as last_update 
                    from `pacc-raw-data.'''+schema+'.'+variable+'_'+component2+'`'+'''
                    where opening_id='''+"'"+opening_id+"'"
    
    a=base_vn.while_loop_page_insert(app='hiring',
                                     schema=schema,
                                     column_name=variable,
                                     job_config=job_config_list,
                                     query_string_incre=query_string,
                                     para1='opening_id',
                                     value1=opening_id,
                                     component2=component2
                                     )