from datetime import datetime
import requests
import time
import pandas as pd
from google.cloud import bigquery
import big_query, pd_process
from base_vn_api import get_base_checkin_api

class base_vn_checkin_flow:
    def __init__(self):
        print('init method called')
             
    def __enter__(self):
        print('enter method called')
        return self
         
    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('exit method called')

    
    def tranform_logs_to_df(self,query_string):
        raw_output = get_base_checkin_api(query_string)
        logs=[sub['logs'] for sub in raw_output['logs']]
        
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
        self.df=self.df.join(pd_process.pd_nested_schema(self.df,'logs',mode='flatten',drop_columns=0)).drop(columns='logs',axis=1)
        
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
        #print(self.final_dataset.dtypes)
        #print(self.final_dataset)
    
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
        result=big_query.bq_insert(schema,table_id,dataframe=self.final_dataset,job_config=job_config_list)
        return result
