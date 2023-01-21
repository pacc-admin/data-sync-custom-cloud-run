from datetime import datetime
import time
import pandas as pd
import sys, os
import numpy as np
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import base_vn,big_query,pd_process

class base_vn_checkin:
    def __init__(self):
        print('init method called')
             
    def __enter__(self):
        print('enter method called')
        return self
         
    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('exit method called')
    
    def check_latest_date_bq(self,query_string):
        self.latest_date_bq=big_query.bq_pandas(query_string)['logs_time'].astype(int).to_list()[0] + 1
        print('latest timestamp on checkin logs is: '+str(self.latest_date_bq))
        return self.latest_date_bq
    
    def get_base_checkin_api(self):
        start_date=self.latest_date_bq
        today_unix = int(time.mktime(datetime.today().timetuple()))

        self.raw_output=base_vn.base_vn_connect(app='checkin',
                                           component1='getlogs',
                                           component2='',
                                           para1='start_date',
                                           value1=start_date,
                                           para2='end_date',
                                           value2=today_unix,                                   
                                        
                                        )
        
        return self.raw_output
    
    def tranform_logs_to_df(self):
        logs=[sub['logs'] for sub in self.raw_output['logs']]
        
        total=[]
        for i in range(len(logs)):
          b=list(logs[i].values())
          total=total+b
        
        self.df=pd.DataFrame(total)
        
        return self.df
            
    def df_process(self):
        #nomalize dictionary columns
        lists=['finalized','computed','stats']
        for item in lists:
          self.df=self.df.join(pd_process.pd_nested_schema(self.df,item)).drop(columns=item,axis=1)
        
        #flatten multi dict columns
        self.df=self.df.join(pd_process.pd_nested_schema(self.df,'logs',mode='flatten')).drop(columns='logs',axis=1)
        
        #add loaded date
        self.df['loaded_date'] = pd.to_datetime('today')
        
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
            'logs_checkout',
            'logs_time',
            'loaded_date'
        ]
        self.df=pd_process.pd_type_change(self.df,columns=non_converted_column_str)

        ##int64
        converted_columns_int=[
            'date',
            'month_index',
            'logs_time'
        ]
        self.df=pd_process.pd_type_change(self.df,columns=converted_columns_int,converted_type=int,type='include')

    def incremental_update(self,query_string):
        self.final_dataset=pd_process.pd_last_update(self.df,query_string,column_updated='logs_time')
        print(self.final_dataset.dtypes)
        print(self.final_dataset)
    
    def bq_batch_load(self,schema,table_id):
        job_config_list = bigquery.LoadJobConfig(
                schema=[
                    bigquery.SchemaField("id",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("user_id",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("employee_id",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("date",bigquery.enums.SqlTypeNames.INT64),
                    bigquery.SchemaField("month_index",bigquery.enums.SqlTypeNames.INT64),
                    bigquery.SchemaField("timesheet_id",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("hid",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("token",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("type",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("stats_comments",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_checkout",bigquery.enums.SqlTypeNames.FLOAT64),
                    bigquery.SchemaField("logs_client_id",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_content",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_files",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_img",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_ip",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_lat",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_lng",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_metatype",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_note",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_office_id",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_photo",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("logs_time",bigquery.enums.SqlTypeNames.INT64),
                    bigquery.SchemaField("logs_office_id",bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP),
                    
                  ]
        )
        big_query.bq_insert(schema,table_id,dataframe=self.final_dataset,job_config=job_config_list)

    
#varible declaration
schema='BASEVN_CHECKIN'
table_id='checkin_logs'
query_string='select max(logs_time) as logs_time from `pacc-raw-data.'+schema+'.'+table_id+'`'

with base_vn_checkin() as s:
    s.check_latest_date_bq(query_string)
    s.get_base_checkin_api()
    s.tranform_logs_to_df()
    s.df_process()
    s.incremental_update(query_string)
    s.bq_batch_load(schema,table_id)
