import pandas as pd
import pyodbc
from big_query import bq_insert,bq_delete

class mssql_bq_dedup:
    def __init__(self,
                 unique_id,
                 branch_schema,
                 mssql_database,
                 mssql_table,
                 bq_schema,
                 bq_table_id_dedup,
                 bq_table_id
        ):
        self.unique_id=unique_id
        self.branch_schema=branch_schema
        self.mssql_database=mssql_database
        self.mssql_table=mssql_table
        self.bq_schema=bq_schema
        self.bq_table_id_dedup=bq_table_id_dedup
        self.bq_table_id=bq_table_id

        print('init method called')
             
    def __enter__(self):
        print('enter method called')
        return self
         
    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('exit method called')

    def connect_to_mssql(self):
        print('step 1')
        server = '180.93.172.68'
        username = 'namba' 
        password = 'R2YUUCR7xN4aF5'
        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';PORT=1433;UID='+username+';PWD='+ password+';TrustServerCertificate=yes;')
        self.conn = conn

    def mssql_query_pd(self):
        print('step 2')
        query = '''SELECT
                        cast('''+self.branch_schema+''' as varchar)+cast(cast('''+self.unique_id+''' as int) as varchar) as unique_id
                    FROM ''' +self.mssql_database+'''.dbo.'''+self.mssql_table+'''
                    WHERE MONTH(tran_date) >= MONTH(GETDATE()) - 1
                        AND YEAR(tran_date) = YEAR(GETDATE())
                '''
        
        print(query)
        df = pd.DataFrame()    
        df = pd.read_sql(query, self.conn)
        self.dataframe = df
    
    def bq_delete_insert_warehouse_dedup(self):
        print('step 4')
        bq_delete(schema=self.bq_schema,table_id=self.bq_table_id_dedup)
        bq_insert(schema=self.bq_schema,table_id=self.bq_table_id_dedup,dataframe=self.dataframe)


    def bq_dedup_warehouse(self):
        print('step 5')
        condition = '''date(date_trunc(parse_timestamp('%FT%H:%M:%E*S%Ez', tran_date),month)) >= date_trunc(date_sub(current_date(),interval 1 month),month)
                            and concat('''+self.branch_schema+''','''+self.unique_id+''') not in (select distinct
                                                            unique_id 
                                                        from pacc-raw-data.'''+self.bq_schema+'''.'''+self.bq_table_id_dedup+')'
        print(condition)        
        bq_delete(schema=self.bq_schema,table_id=self.bq_table_id,condition=condition)