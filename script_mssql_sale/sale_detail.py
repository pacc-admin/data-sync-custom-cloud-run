from google.cloud import bigquery
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import big_query
import mssql

#Execution
database = ['IPOSSBGN','IPOSS5WINE']
schema='IPOS_SALE'
date_schema='tran_date'
date_to_delete= 30
table_names = ['sale_detail_bgn','sale_detail_5wine']

condition = "date_diff(current_date,date(tran_date),day) <="+str(date_to_delete)

for database_name,table_name in zip(database,table_names):
    print('---start---')
    print('Loaded from MSSQL:'+database_name+' to BQ:'+table_name)
    big_query.bq_delete(schema,table_name,condition=condition)
    query_string = '''
                with sale as (
                    select
                        sale.pr_key,
                    	sale.tran_date,
                        store.workstation_name
                     
                    from '''+database_name+'''.dbo.sale sale
                    left join '''+database_name+'''.dbo.dm_workstation store
                        on sale.workstation_id = store.workstation_id
                '''
    query_string2 = '''
                )

                select
                    HashBytes('MD5', sale.workstation_name+cast(sale_detail.pr_key as varchar)) as unique_key,
                    sale_detail.*,
                	sale.tran_date,
                	sale.workstation_name,
                    '''+"'"+database_name+'''' as data_source
                
                
                from '''+database_name+'''.dbo.sale_detail sale_detail
                inner join sale
                on sale_detail.fr_key = sale.pr_key
            '''


    job_config_list=bigquery.LoadJobConfig(
        schema = [ 
                   bigquery.SchemaField("LOADED_DATE",bigquery.enums.SqlTypeNames.TIMESTAMP),
                   bigquery.SchemaField("SALE_DATE",bigquery.enums.SqlTypeNames.DATETIME),
                   bigquery.SchemaField("END_DATE",bigquery.enums.SqlTypeNames.DATETIME),
                   bigquery.SchemaField("tran_date",bigquery.enums.SqlTypeNames.DATETIME),
                ]
    )

    mssql.incremental_load_sale(
                          query_string=query_string,
                          schema=schema,
                          table_id=table_name,
                          date_schema=date_schema,
                          query_string2=query_string2,
                          job_config=job_config_list
                        )
    
    print('---end---')