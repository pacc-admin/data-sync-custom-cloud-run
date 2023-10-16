import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import pandas as pd
import base_vn,big_query


#finding opening id
pool_raw=base_vn.base_vn_connect(app='hiring',component1='pool',component2='list')
pool=pool_raw['pools']
pool_ids=[sub['id'] for sub in pool]
print(pool_ids)

#specify other variables
variable='contact'
component2='list'
schema='BASEVN_EHIRING'
stop_words=['candidates']
job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)            
        ]
)


def get_data():
    df=pd.DataFrame()
    for pool_id in pool_ids:
        print(pool_id)
        query_string='''
                        select max(last_update) as last_update 
                        from `pacc-raw-data.'''+schema+'.'+variable+'`'+'''
                        where ns_id='''+"'"+pool_id+"'"
        
        
        df_pool=base_vn.while_loop_page_return(app='hiring',
                                         column_name=variable,
                                         query_string_incre=query_string,
                                         para1='pool_id',
                                         value1=pool_id,
                                         component2=component2,
                                         stop_words=stop_words
                                         )
        df = pd.concat([df,df_pool])
    return df

def condition(df):
    #condition to exclude
    try:
        condition='id in '+"('"+"','".join(df['id'].to_list())+"')"
    except:
        condition='true'
    return condition

try:
    #insert to BQ
    result=big_query.bq_insert(
                schema,
                table_id=variable,
                dataframe=get_data(),
                condition=condition(get_data()),
                job_config=job_config_list,
                unique_key='id'
            )
except:
    print("recreate table")
    query_string = 'create or replace table '+schema+'.'+variable+' (id string, loaded_date timestamp)'
    big_query.bq_query(query_string)    
    result=big_query.bq_insert(
                schema,
                table_id=variable,
                dataframe=get_data(),
                condition=condition(get_data()),
                job_config=job_config_list,
                unique_key='id'
            )
    
print(result)

