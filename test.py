import pandas as pd
import pyodbc
from google.cloud import bigquery
import os

#Setting Sql server credential in environment
server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
username=os.environ.get("MSSQL_SALE_IP_USERNAME")
password=os.environ.get("MSSQL_SALE_IP_PASSWORD")

#Setting BQ project in environment
os.environ.setdefault("GCLOUD_PROJECT", 'pacc-raw-data')
service_account_file_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

class mssql_bq:
    #SQL Server
    def connect_to_mssql(self):
        print('step 1')
        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
        self.conn = conn
        print('end step 1')
        
    def mssql_query_pd(self,query_string):
        print('step 2')
        query = query_string
        
        df = pd.DataFrame()    
        df = pd.read_sql(query, self.conn)
        self.dataframe = df
        if df.to_dict('records')==[]:
            result='end'
        else:
            result='continue'
        return result

    
database = ['IPOSS5WINE']

if __name__ == '__main__':
    for database_name in database:
        print(database_name)
        dataset_name = 'sale'
        print(dataset_name)
        
        query_string = '''SELECT
                    a.*,
                    b.workstation_name
                 
                from '''+database_name+'''.dbo.sale a
                left join '''+database_name+'''.dbo.dm_workstation b
                    on a.workstation_id = b.workstation_id
                    where dateadd(day, datediff(day, 0, tran_date), 0) = dateadd(day,-1,dateadd(day, datediff(day, 0, getdate()), 0))
                '''

        s = mssql_bq()
        s.connect_to_mssql()
        s.mssql_query_pd(query_string)
        if s.mssql_query_pd(query_string)=='end':
            print('stop')
        else:
            print(s.connect_to_mssql())
