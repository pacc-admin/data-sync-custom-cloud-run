from google.cloud import bigquery
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import big_query,mssql
from datetime import date
from datetime import timedelta

#Setting Sql server credential in environment
server=os.environ.get("MSSQL_SALE_IP_ADDRESS")
username=os.environ.get("MSSQL_SALE_IP_USERNAME")
password=os.environ.get("MSSQL_SALE_IP_PASSWORD")

#Function prep
def mssql_bq_insert(query_string,schema,table_id,job_config= bigquery.LoadJobConfig()):
    #MSSQL
    print('step 1')
    dataframe = mssql.mssql_query_pd(server,username,password,query_string)
    if dataframe.to_dict('records')==[]:
        print('end')
    else:
        print('continue')
        #BQ
        print('step 2')
        client=big_query.connect_to_bq()
        print('step 3')
        big_query.bq_insert(client,schema,table_id,dataframe,job_config)

#Execution
database = ['IPOSSBGN','IPOSS5WINE']
schema='IPOS_SALE'

#finding latest date from BQ table
df=big_query.bq_pandas(query_string='select max(cast(tran_date as date)) as tran_date from `pacc-raw-data.IPOS_SALE.sale_detail`')
recent_loaded_date=df['tran_date'].astype(str).to_list()[0]

##Sale
for database_name in database:
    theory_loaded_date=date.today() - timedelta(days = 1)
    table_name = 'sale_detail'
    
    #finding max pr key from BQ table
    df2=big_query.bq_pandas(
        query_string= "select distinct cast(fr_key as int64) as pr_key from `pacc-raw-data."+schema+".sale_detail` where data_source='"+database_name+"'and date(tran_date) = '"+recent_loaded_date+"'")

    pr_key_latest="('"+"','".join(df2['pr_key'].astype(str).to_list())+"')"

    #dynamic condition by latest tran date
    if str(theory_loaded_date)==recent_loaded_date:
        condition="cast(sale.tran_date as date) = '"+recent_loaded_date+"' and cast(cast(pr_key as int) as varchar) not in "+pr_key_latest     
    else:
        condition="cast(sale.tran_date as date) > '"+recent_loaded_date+"'"

    query_string = '''SELECT
                HashBytes('MD5', workstation.workstation_name+cast(sale.pr_key as varchar)) as unique_key,
                getdate() as updated_date,
                sale.*,
                workstation.workstation_name,
                '''+"'"+database_name+'''' as data_source

             
            from '''+database_name+'''.dbo.sale sale
            left join '''+database_name+'''.dbo.dm_workstation workstation
                on sale.workstation_id = workstation.workstation_id
            where '''+condition


    job_config_list = bigquery.LoadJobConfig(
        schema = [ 
                   bigquery.SchemaField("updated_date",bigquery.enums.SqlTypeNames.TIMESTAMP),
                   bigquery.SchemaField("SALE_DATE",bigquery.enums.SqlTypeNames.TIMESTAMP),
                   bigquery.SchemaField("END_DATE",bigquery.enums.SqlTypeNames.TIMESTAMP),
                   bigquery.SchemaField("tran_date",bigquery.enums.SqlTypeNames.TIMESTAMP),
                ]
    
    )
    query_string = '''
                with sale as (
                    select
                        sale.pr_key,
                    	sale.tran_date,
                        store.workstation_name
                     
                    from '''+database_name+'''.dbo.sale sale
                    left join '''+database_name+'''.dbo.dm_workstation store
                        on sale.workstation_id = store.workstation_id
                    where '''+condition+'''
                )
                
                select
                    HashBytes('MD5', sale.workstation_name+cast(sale_detail.pr_key as varchar)) as unique_key,
                    getdate() as updated_date,
                    sale_detail.*,
                	sale.tran_date,
                	sale.workstation_name,
                    '''+"'"+database_name+'''' as data_source
                
                
                from '''+database_name+'''.dbo.sale_detail sale_detail
                inner join sale
                on sale_detail.fr_key = sale.pr_key
            '''
    print(query_string)
    mssql_bq_insert(query_string,schema,table_name,job_config=job_config_list)

