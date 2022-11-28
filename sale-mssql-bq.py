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
    if dataframe.to_dict('records')==[]:
        print('end')
    else:
        print('continue')
        #BQ
        print('step 2')
        client=dbconnector.connect_to_bq()
        print('step 3')
        dbconnector.bq_insert(client,schema,table_id,dataframe)


#Execution
database = ['IPOSSBGN','IPOSS5WINE']
schema='IPOS_SALE'

##Sale
for database_name in database:
    table_name = 'sale'
    query_string = '''SELECT
                HashBytes('MD5', workstation.workstation_name+cast(sale.pr_key as varchar)) as unique_key,
                getdate() as updated_date,
                sale.*,
                workstation.workstation_name
             
            from '''+database_name+'''.dbo.sale sale
            left join '''+database_name+'''.dbo.dm_workstation workstation
                on sale.workstation_id = workstation.workstation_id
            where dateadd(day, datediff(day, 0, sale.tran_date), 0) = dateadd(day,-1,dateadd(day, datediff(day, 0, getdate()), 0))
            '''
    mssql_bq_insert(query_string,schema,table_name)

##Sale_detail
for database_name in database:
    table_name = 'sale_detail'
    query_string = '''
                with sale as (
                    select
                        sale.pr_key,
                    	sale.tran_date,
                        store.workstation_name
                     
                    from '''+database_name+'''.dbo.sale sale
                    left join '''+database_name+'''.dbo.dm_workstation store
                        on sale.workstation_id = store.workstation_id
                    where dateadd(day, datediff(day, 0, sale.tran_date), 0) = dateadd(day,-1,dateadd(day, datediff(day, 0, getdate()), 0))
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
    mssql_bq_insert(query_string,schema,table_name)
