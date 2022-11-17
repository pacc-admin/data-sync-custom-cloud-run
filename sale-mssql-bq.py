import pandas as pd
import pyodbc
from google.cloud import bigquery
import os

#Setting Sql server credential in environment
server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
username=os.environ.get("MSSQL_SALE_IP_USERNAME")
password=os.environ.get("MSSQL_SALE_IP_PASSWORD")

#Setting BQ credential in environment
os.environ.setdefault("GCLOUD_PROJECT", 'pacc-raw-data')
service_account_file_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

class mssql_bq:
    #SQL Server
    def connect_to_mssql(self):
        print('step 1')
        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
        self.conn = conn
        
    def mssql_query_pd(self,query_string):
        print('step 2')
        query = query_string
        
        df = pd.DataFrame()    
        df = pd.read_sql(query, self.conn)
        self.dataframe = df

        #checking
        self.dataframe = df
        if df.to_dict('records')==[]:
            result='end'
        else:
            result='continue'
        return result
    
    #BQ
    def connect_to_bq(self):
        print('step 3')
        self.client = bigquery.Client.from_service_account_json(service_account_file_path)

    def bq_insert(self,dataset_name):
        print('step 4')
        table_id = 'pacc-raw-data.IPOS_SALE.'+dataset_name
        job_config = bigquery.LoadJobConfig()
        job_config._properties['load']['schemaUpdateOptions'] = ['ALLOW_FIELD_ADDITION']
    
        job = self.client.load_table_from_dataframe(
            self.dataframe, table_id, job_config=job_config
        )
        job.result()
        
        table =  self.client.get_table(table_id)
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )

database = ['IPOSSBGN','IPOSS5WINE']

if __name__ == '__main__':
    s = mssql_bq()
    s.connect_to_mssql()
    s.connect_to_bq() 
    for database_name in database:
        print(database_name)
        dataset_name = 'sale'
        print(dataset_name)
        
        query_string = '''SELECT
                    HashBytes('MD5', workstation.workstation_name+cast(sale.pr_key as varchar)) as unique_key,
                    getdate() as updated_date,
                    sale.*,
                    workstation.workstation_name
                 
                from '''+database_name+'''.dbo.sale sale
                left join '''+database_name+'''.dbo.dm_workstation workstation
                    on sale.workstation_id = workstation.workstation_id
                where year(sale.tran_date) > 2019
                --where dateadd(day, datediff(day, 0, sale.tran_date), 0) = dateadd(day,-1,dateadd(day, datediff(day, 0, getdate()), 0))
                '''

        s.mssql_query_pd(query_string)
        if s.mssql_query_pd(query_string)=='end':
            print('stop')
        else:
            s.bq_insert(dataset_name)

#Sale_detail
if __name__ == '__main__':
    s = mssql_bq()
    s.connect_to_mssql()
    s.connect_to_bq() 
    for database_name in database:
        print(database_name)
        dataset_name = 'sale_detail'
        print(dataset_name)

        query_string = '''
                    with sale as (
                        select
                            sale.pr_key,
                        	sale.tran_date,
                            store.workstation_name
                         
                        from '''+database_name+'''.dbo.sale sale
                        left join '''+database_name+'''.dbo.dm_workstation store
                            on sale.workstation_id = store.workstation_id
                        where dateadd(day, datediff(day, 0, tran_date), 0) = dateadd(day,-1,dateadd(day, datediff(day, 0, getdate()), 0))
                    )
                    
                    select
                        HashBytes('MD5', sale.workstation_name+cast(sale_detail.pr_key as varchar)) as unique_key,
                        getdate() as updated_date,
                        sale_detail.*,
                    	sale.tran_date,
                    	sale.workstation_name
                    
                    
                    from '''+database_name+'''.dbo.sale_detail sale_detail
                    inner join sale
                    on sale_detail.fr_key = sale.pr_key
                '''

        s.mssql_query_pd(query_string)
        if s.mssql_query_pd(query_string)=='end':
            print('stop')
        else:
            s.bq_insert(dataset_name)
