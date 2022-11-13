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
        server = '180.93.172.68'
        username = 'namba' 
        password = 'S%f2L5^4W2w8'
        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
        self.conn = conn
        
    def mssql_query_pd(self,database_name):
        print('step 2')
        query = '''SELECT
                        cast(WAREHOUSE_ID as varchar)+cast(cast(PR_KEY_WAREHOUSE as int) as varchar) as unique_id, 
                        convert(varchar(10),cast(tran_date as date),126) as tran_date
                    FROM [''' +database_name+'''].[dbo].[WAREHOUSE]
                    WHERE MONTH(tran_date) >= MONTH(GETDATE()) - 1
                        AND YEAR(tran_date) = YEAR(GETDATE())
                '''
        
        df = pd.DataFrame()    
        df = pd.read_sql(query, self.conn)
        self.dataframe = df
    
    #BQ
    def connect_to_bq(self):
        print('step 3')
        project_id = 'pacc-raw-data'
        self.client = bigquery.Client.from_service_account_json(service_account_file_path)


    def bq_delete_warehouse_dedup(self,dataset_name):
        print('step 4')
        self.table_id_dedup = 'pacc-raw-data.'+dataset_name+'.warehouse_dedup'
        query = 'Delete from '+self.table_id_dedup+' where true'
        query_job = self.client.query(query)
        results1 = query_job.result()
        print(results1)

    def bq_insert_warehouse_dedup(self):
        print('step 5')
        table_id = self.table_id_dedup
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

    def bq_dedup_warehouse(self,dataset_name):
        print('step 6')
        table_id = 'pacc-raw-data.'+dataset_name+'.2022_WAREHOUSE_ANALYTICS'
        query = '''Delete from '''+table_id+''' 
                       where date(date_trunc(parse_timestamp('%FT%H:%M:%E*S%Ez', tran_date),month)) >= date_trunc(date_sub(current_date(),interval 1 month),month)
                            and concat(warehouse_id,PR_KEY_WAREHOUSE) not in (select distinct
                                                            unique_id 
                                                        from '''+self.table_id_dedup+')'
                
                
        query_job = self.client.query(query)
        print(query_job.result())

database = ['IACC_BGPACC2022','IACC_BGPACCBAUCAT2022']
dataset = ['PACC_ALL','PACC_BAUCAT']

if __name__ == '__main__':
    for (database_name,dataset_name) in zip(database,dataset):
        print(database_name)
        print(dataset_name)
        s = mssql_bq()
        s.connect_to_mssql()
        s.mssql_query_pd(database_name)
        s.connect_to_bq()
        s.bq_delete_warehouse_dedup(dataset_name)
        s.bq_insert_warehouse_dedup()
        s.bq_dedup_warehouse(dataset_name)
