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
        print('step 3')
        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
        self.conn = conn

    def mssql_query_pd(self,database_name,query_string):
        print('step 4')
        query = query_string

        print(query)
        df = pd.DataFrame()    
        df = pd.read_sql(query, self.conn)
        self.dataframe = df
    
    #BQ
    def connect_to_bq(self):
        print('step 1')
        project_id = 'pacc-raw-data'
        self.client = bigquery.Client.from_service_account_json(service_account_file_path)


    def bq_delete(self,table_name):
        print('step 2')
        self.table_id = 'pacc-raw-data.IPOS_SALE.'+table_name
        query = 'Delete from '+self.table_id+' where true'
        query_job = self.client.query(query)
        results1 = query_job.result()
        print(results1)

    def bq_insert(self):
        print('step 5')
        table_id = self.table_id
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


database = ['IPOSS5WINE','IPOSSBGN']

if __name__ == '__main__':
    table_name='dm_extra_2'
    s = mssql_bq()
    s.connect_to_bq()
    s.bq_delete(table_name) 
    for database_name in database:
        print(table_name)
        print(database_name)
        query_string = "select *, "+"'"+database_name+"'"+' as data_source from '+database_name+'.dbo.'+table_name
        
        s.connect_to_mssql()
        s.mssql_query_pd(database_name,query_string)  
        s.bq_insert()

if __name__ == '__main__':
    table_name='dm_item'
    s = mssql_bq()
    s.connect_to_bq()
    s.bq_delete(table_name) 
    for database_name in database:
        print(table_name)
        print(database_name)
        query_string = '''
                        with item_grouped as (
                            select
                                 item_type_id,
                                 item_type_name,
                            	 row_number() over (partition by item_type_id order by item_type_name desc) as rn
                            
                            from '''+database_name+'''.dbo.dm_item_type
                            where active = 1
                        ),
                        
                        item_cat as (
                            select distinct
                                 item_class_id,
                                 item_class_name
                            
                            from '''+database_name+'''.dbo.dm_item_class
                        )

                        select  
                            item.*,
                            item_cat.item_class_name as item_category,
                            item_grouped.item_type_name as item_group,
                            '''+"'"+database_name+"'"+''' as data_source
                        
                        from '''+database_name+'.dbo.'+table_name+''' item
                        left join item_cat
                            on item.item_class_id = item_cat.item_class_id
                        left join item_grouped
                            on item.item_type_id = item_grouped.item_type_id
                            and rn = 1
                        '''
        
        s.connect_to_mssql()
        s.mssql_query_pd(database_name,query_string)  
        s.bq_insert()