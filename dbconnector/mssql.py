from big_query import bq_insert,bq_delete,bq_pandas,bq_latest_date
from google.cloud import bigquery
import pyodbc
import pandas as pd
import os
from datetime import date
from datetime import timedelta

def mssql_query_pd(query_string):
    server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
    username=os.environ.get("MSSQL_SALE_IP_USERNAME")
    password=os.environ.get("MSSQL_SALE_IP_PASSWORD")

    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;Encrypt=yes')
    query = query_string
    df = pd.DataFrame()    
    df = pd.read_sql(query, conn)
    return df

def mssql_query_pd_sale(query_string):
    df = mssql_query_pd(query_string)

    #convert date column to datetime
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    for col in date_cols: 
       df[col] = pd.to_datetime(df[col], format='%d/%m/%y')

    df['LOADED_DATE'] = pd.to_datetime('today', format='%Y-%m-%d %H:%M:%S.%f')
    print(df.head(5))

    return df

def full_refresh_sale(query_string,schema,table_id,condition='true'):
    print('step 1')
    dataframe = mssql_query_pd_sale(query_string)
    print('step 2')
    bq_insert(schema,table_id,dataframe,condition=condition)


def incremental_load_sale(query_string,
                          schema,
                          table_id,
                          date_schema,
                          query_string2='',
                          table_filter_date='sale', 
                          job_config=bigquery.LoadJobConfig()
                        ):
    #MSSQL
    print('step 1')
    today=date.today()
    recent_loaded_date=bq_latest_date(date_schema,schema=schema,table_id=table_id)

    print('step 2')
    #finding list of pr key in latest day
    df2=bq_pandas(
        query_string= "select cast(pr_key as int64) as pr_key from `pacc-raw-data."+schema+"."+table_id+"` where date("+date_schema+") = '"+str(today)+"'"
        )
    pr_key_latest="('"+"','".join(df2['pr_key'].astype(str).to_list())+"')"

    #dynamic incre_condition by latest tran date
    if query_string2=='':
        table_filter_date=table_id
    else:
        table_filter_date=table_filter_date
    
    if str(today)==recent_loaded_date:
        incre_condition="cast("+table_filter_date+"."+date_schema+" as date) = '"+recent_loaded_date+"' and cast(cast(pr_key as int) as varchar) not in "+pr_key_latest 
    else:
        incre_condition="cast("+table_filter_date+"."+date_schema+" as date) > '"+recent_loaded_date+"'"

    query_string_insert=query_string+'where '+incre_condition+query_string2

    dataframe = mssql_query_pd_sale(query_string_insert)
    if dataframe.to_dict('records')==[]:
        print('end')
    else:
        print('continue')
        #BQ
        print('step 3')
        bq_insert(schema,table_id,dataframe,job_config=job_config)
        print('end')
