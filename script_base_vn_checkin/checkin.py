from datetime import datetime
import time
import pandas as pd
import sys, os
import json
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn,big_query


app='checkin'
today_unix = int(time.mktime(datetime.today().timetuple()))
raw_output=base_vn.base_vn_connect(app,
                                   component1='getlogs',
                                   component2='',
                                   para1='start_date',
                                   value1='1669852800',
                                   para2='end_date',
                                   value2=today_unix,                                   
                                
                                )


logs=[sub['logs'] for sub in raw_output['logs']]

total=[]
for i in range(len(logs)):
  b=list(logs[i].values())
  total=total+b

df=pd.DataFrame(total)

def flatten_json_schema(df,column):
  flatten=pd.json_normalize(df[column])
  flatten.columns = column+'_' + flatten.columns
  return flatten

lists=['finalized','computed','stats']

for item in lists:
  #print(item)
  print(flatten_json_schema(df,item).dtypes)
  df=df.join(flatten_json_schema(df,item)).drop(columns=item,axis=1)

df['loaded_date'] = pd.to_datetime('today')
df['logs']=df['logs'].astype(str)
print(df.dtypes)

job_config_list = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP),
            bigquery.SchemaField("finalized_day_point",bigquery.enums.SqlTypeNames.FLOAT64),
            bigquery.SchemaField("logs",bigquery.enums.SqlTypeNames.STRING)
        ]
)

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
big_query.bq_insert(schema='BASEVN_CHECKIN',table_id='checkin_logs',dataframe=df,job_config=job_config_list)
