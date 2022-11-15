import pandas as pd
import pyodbc
from google.cloud import bigquery
import os

#Setting BQ project in environment
os.environ.setdefault("GCLOUD_PROJECT", 'pacc-raw-data')
service_account_file_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

class mssql_bq:
    #SQL Server
    def connect_to_mssql(self):
        print('step 1')
        server = '180.93.172.30'
        username = 'namba' 
        password = '32UvRL9Om@VH'
        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
        self.conn = conn
        print('end step 1')
        
    def mssql_query_pd(self,query_string):
        print('step 2')
        query = query_string
        
        df = pd.DataFrame()    
        df = pd.read_sql(query, self.conn)
        self.dataframe = df
        print('end step 2')
    
    #BQ
    def connect_to_bq(self):
        print('step 3')
        self.client = bigquery.Client.from_service_account_json(service_account_file_path)
        print('end step 3')

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
        print('end step 4')

database = ['IPOSS5WINE']
#,' IPOSSBGN'
#Sale
#if __name__ == '__main__':
#    for database_name in database:
#        print(database_name)
#        dataset_name = 'sale_detail'
#        print(dataset_name)
#        
#        query_string = '''SELECT top 1
#                    a.*,
#                    b.workstation_name
#                 
#                from '''+database_name+'''.dbo.sale a
#                left join '''+database_name+'''.dbo.dm_workstation b
#                    on a.workstation_id = b.workstation_id
#                    where 1=1
#                '''
#
#        s = mssql_bq()
#        s.connect_to_mssql()
#        s.mssql_query_pd(query_string)
#        #s.connect_to_bq()
#        #s.bq_insert(dataset_name)


#Sale_detail
if __name__ == '__main__':
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
                        where year(tran_date) <= 2019
                    )
                    
                    select
                        sale_detail.*,
                    	sale.tran_date,
                    	sale.workstation_name
                    
                    
                    from '''+database_name+'''.dbo.sale_detail sale_detail
                    inner join sale
                    on sale_detail.fr_key = sale.pr_key
                '''
        print(query_string)
        s = mssql_bq()
        s.connect_to_mssql()
        s.mssql_query_pd(query_string)
        s.connect_to_bq()
        s.bq_insert(dataset_name)

