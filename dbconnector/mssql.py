from big_query import bq_insert,bq_delete,bq_pandas,bq_latest_date
from google.cloud import bigquery
import pyodbc
import pandas as pd
import os
from datetime import date
from datetime import timedelta

def mssql_query_pd(server,username,password,query_string):
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
    query = query_string
    print(query)
    df = pd.DataFrame()    
    df = pd.read_sql(query, conn)
    dataframe = df

    #convert date column to datetime
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    for col in date_cols: 
       df[col] = pd.to_datetime(df[col], utc=False)

    df['LOADED_DATE'] = pd.to_datetime('today')
    print(df.head(10))
    return dataframe

def mssql_query_pd_sale(query_string):
    server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
    username=os.environ.get("MSSQL_SALE_IP_USERNAME")
    password=os.environ.get("MSSQL_SALE_IP_PASSWORD")
    dataframe = mssql_query_pd(server,username,password,query_string)
    return dataframe

def full_refresh_sale(query_string,schema,table_id):
    server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
    username=os.environ.get("MSSQL_SALE_IP_USERNAME")
    password=os.environ.get("MSSQL_SALE_IP_PASSWORD")

    print('step 1')
    dataframe = mssql_query_pd(server,username,password,query_string)
    print('step 2')
    bq_insert(schema,table_id,dataframe)


def incremental_load_sale(query_string,
                          mssql_database_name,
                          schema,
                          table_id,
                          date_schema,
                          query_string2='',
                          table_filter_date='sale', 
                          job_config= bigquery.LoadJobConfig()
                        ):
    #MSSQL
    print('step 1')
    today=date.today()
    recent_loaded_date=bq_latest_date(date_schema,schema=schema,table_id=table_id)

    print('step 2')
    #finding list of pr key in latest day
    df2=bq_pandas(
        query_string= "select cast(pr_key as int64) as pr_key from `pacc-raw-data."+schema+"."+table_id+"` where data_source='"+mssql_database_name+"'and date("+date_schema+") = '"+str(today)+"'"
        )
    pr_key_latest="('"+"','".join(df2['pr_key'].astype(str).to_list())+"')"

    #dynamic condition by latest tran date
    if query_string2=='':
        table_filter_date=table_id
    else:
        table_filter_date=table_filter_date
    
    if str(today)==recent_loaded_date:
        condition="cast("+table_filter_date+"."+date_schema+" as date) = '"+recent_loaded_date+"' and cast(cast(pr_key as int) as varchar) not in "+pr_key_latest 
    else:
        condition="cast("+table_filter_date+"."+date_schema+" as date) > '"+recent_loaded_date+"'"
        print("yes")

    query_string_insert=query_string+'where '+condition+query_string2
    print(query_string_insert)

    dataframe = mssql_query_pd_sale(query_string_insert)
    if dataframe.to_dict('records')==[]:
        print('end')
    else:
        print('continue')
        #BQ
        print('step 3')
        bq_insert(schema,table_id,dataframe,job_config)
        print('end')
