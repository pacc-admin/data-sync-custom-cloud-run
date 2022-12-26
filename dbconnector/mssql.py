from big_query import connect_to_bq,bq_insert,bq_delete
import pyodbc
import pandas as pd
import os

#connect to bq
client=connect_to_bq()

def mssql_query_pd(server,username,password,query_string):
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
    query = query_string
    print(query)
    df = pd.DataFrame()    
    df = pd.read_sql(query, conn)
    dataframe = df
    return dataframe


def full_refresh_sale(query_string,schema,table_id):
    server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
    username=os.environ.get("MSSQL_SALE_IP_USERNAME")
    password=os.environ.get("MSSQL_SALE_IP_PASSWORD")

    print('step 1')
    dataframe = mssql_query_pd(server,username,password,query_string)
    print('step 2')
    bq_insert(client,schema,table_id,dataframe)