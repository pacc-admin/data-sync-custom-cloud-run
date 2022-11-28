import pandas as pd
import dbconnector
import os

#Setting Sql server credential in environment
server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
username=os.environ.get("MSSQL_SALE_IP_USERNAME")
password=os.environ.get("MSSQL_SALE_IP_PASSWORD")

#Function prep
def mssql_bq_insert(query_string,schema,table_id):
    #MSSQL
    print('step 1')
    dataframe = dbconnector.mssql_query_pd(server,username,password,query_string)
    #BQ
    print('step 2')
    client=dbconnector.connect_to_bq()
    print('step 3')
    dbconnector.bq_delete(client,schema,table_id)
    print('step 4')
    dbconnector.bq_insert(client,schema,table_id,dataframe)

#Execution
database = ['IPOSS5WINE','IPOSSBGN']
schema='IPOS_SALE'
for database_name in database:
    table_name='dm_extra_2'
    query_string = "select *, "+"'"+database_name+"'"+' as data_source from '+database_name+'.dbo.'+table_name
    mssql_bq_insert(query_string,schema,table_name)

for database_name in database:
    table_name='dm_item'
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
    mssql_bq_insert(query_string,schema,table_name)
