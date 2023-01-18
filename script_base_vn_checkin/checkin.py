from datetime import datetime
import time
import pandas as pd
import sys, os
import numpy as np
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn,big_query,pd_process

#varible declaration
app='checkin'
schema='BASEVN_CHECKIN'
table_id='checkin_logs'
today_unix = int(time.mktime(datetime.today().timetuple()))

query_string='select max(logs_time) as logs_time from `pacc-raw-data.'+schema+'.'+table_id+'`'
latest_date_bq=big_query.bq_pandas(query_string)['logs_time'].astype(int).to_list()[0] + 1
print(latest_date_bq)
#Get checklog api result
raw_output=base_vn.base_vn_connect(app,
                                   component1='getlogs',
                                   component2='',
                                   para1='start_date',
                                   value1=latest_date_bq,
                                   para2='end_date',
                                   value2=today_unix,                                   
                                
                                )

#process logs
logs=[sub['logs'] for sub in raw_output['logs']]

total=[]
for i in range(len(logs)):
  b=list(logs[i].values())
  total=total+b

df=pd.DataFrame(total)

#nomalize dictionary columns
lists=['finalized','computed','stats']
for item in lists:
  df=df.join(pd_process.pd_nested_schema(df,item)).drop(columns=item,axis=1)

#flatten multi dict columns
df=df.join(pd_process.pd_nested_schema(df,'logs',mode='flatten')).drop(columns='logs',axis=1)

#add loaded date
df['loaded_date'] = pd.to_datetime('today')

#convert type
##string
non_converted_column_str=[
    'date',
    'month_index',
    'timesheet_id',
    'computed_is_late',
    'computed_day_point',
    'computed_sum_minute_late',
    'computed_sum_late',
    'finalized_is_late',
    'finalized_day_point',
    'finalized_sum_minute_late',
    'finalized_sum_late',
    'stats_comments',
    'logs_checkout',
    'logs_time',
    'loaded_date'
]
df=pd_process.pd_type_change(df,columns=non_converted_column_str)

##int64
converted_columns_int=[
    'date',
    'month_index',
    'logs_time'
]
df=pd_process.pd_type_change(df,columns=converted_columns_int,converted_type=int,type='include')


#incremental update
final_dataset=pd_process.pd_last_update(df,query_string,column_updated='logs_time')
print(final_dataset)

#BQ batchload
job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP),
            bigquery.SchemaField("finalized_day_point",bigquery.enums.SqlTypeNames.FLOAT64)
          ]
)

big_query.bq_insert(schema,table_id,dataframe=final_dataset,job_config=job_config_list)

#job_config_list = bigquery.LoadJobConfig(
#        schema=[
#            #bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP),
#            bigquery.SchemaField(
#                "logs",
#                "RECORD",
#                mode="REPEATED",
#                fields=[
#                    bigquery.SchemaField("ip", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("client_id", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("office_id", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("time", "int64", mode="NULLABLE"),
#                    bigquery.SchemaField("metatype", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("numberOfYears", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("lat", "string", mode="NULLABLE"),
#                    bigquery.SchemaField("lng", "string", mode="NULLABLE"),
#                    bigquery.SchemaField("img", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("checkout", "int64", mode="NULLABLE"),
#                    bigquery.SchemaField("note", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("files", "INT64", mode="REPEATED"),
#                    bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
#                    bigquery.SchemaField("photo", "STRING", mode="NULLABLE")
#                ]
#            ),
#            bigquery.SchemaField(
#                "finalized",
#                "RECORD",
#                mode="NULLABLE",
#                fields=[
#                    #bigquery.SchemaField("is_late", "string", mode="NULLABLE"),
#                    #bigquery.SchemaField("day_point", "string", mode="NULLABLE"),
#                    #bigquery.SchemaField("sum_minute_late", "string", mode="NULLABLE"),
#                    #bigquery.SchemaField("sum_late", "string", mode="NULLABLE"),
#                    bigquery.SchemaField(
#                      "shift_info", 
#                      "RECORD", 
#                      mode="REPEATED",
#                      fields=[
#                          bigquery.SchemaField("shift_point", "float64", mode="NULLABLE"),
#                          bigquery.SchemaField("is_late", "int64", mode="NULLABLE"),
#                          bigquery.SchemaField("late", "int64", mode="NULLABLE"),
#                          bigquery.SchemaField("min_early", "int64", mode="NULLABLE"),
#                          bigquery.SchemaField("deduction", "int64", mode="NULLABLE"),
#                          bigquery.SchemaField("not_checkout", "int64", mode="NULLABLE"),
#                          bigquery.SchemaField("shift_index", "int64", mode="NULLABLE"),
#                          bigquery.SchemaField("type_id", "STRING", mode="NULLABLE"),
#                          bigquery.SchemaField("metatype", "STRING", mode="NULLABLE"),
#                          bigquery.SchemaField("assigned_shift_id", "int64", mode="NULLABLE")
#                      ]
#                    )  
#                ]
#          )
#        ]
#)