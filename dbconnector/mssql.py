import pyodbc
import pandas as pd
import os

def mssql_query_pd(server,username,password,query_string):
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
    query = query_string
    print(query)
    df = pd.DataFrame()    
    df = pd.read_sql(query, conn)
    dataframe = df
    return dataframe