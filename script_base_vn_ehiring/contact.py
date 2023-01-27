import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn


#finding opening id
pool_raw=base_vn.base_vn_connect(app='hiring',component1='pool',component2='list')
pool=pool_raw['pools']
pool_ids=[sub['id'] for sub in pool]
print(pool_ids)

#specify other variables
variable='contact'
component2='list'
schema='BASEVN_EHIRING'
stop_words=['candidates','files']
job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)            
        ]
)

for pool_id in pool_ids:
    print(pool_id)
    query_string='''
                    select max(last_update) as last_update 
                    from `pacc-raw-data.'''+schema+'.'+variable+'`'+'''
                    where ns_id='''+"'"+pool_id+"'"
    
    a=base_vn.while_loop_page_insert(app='hiring',
                                     schema=schema,
                                     column_name=variable,
                                     job_config=job_config_list,
                                     query_string_incre=query_string,
                                     para1='pool_id',
                                     value1=pool_id,
                                     component2=component2,
                                     stop_words=stop_words
                                     )