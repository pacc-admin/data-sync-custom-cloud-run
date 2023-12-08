from google.cloud import bigquery
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import mssql
import big_query

database = ['IPOSSBGN','IPOSS5WINE']
schema='IPOS_SALE'
date_schema='tran_date'
date_to_delete= 30
table_names = ['sale_bgn','sale_5wine']

condition = "date_diff(current_date,date("+date_schema+"),day) <="+str(date_to_delete)

for database_name,table_name in zip(database,table_names):
    print('---start---')
    print('Loaded from MSSQL:'+database_name+' to BQ:'+table_name)
    big_query.bq_delete(schema,table_name,condition=condition)
    query_string = '''SELECT
                HashBytes('MD5', workstation.workstation_name+cast(sale.pr_key as varchar)) as unique_key,
                sale.*,
                workstation.workstation_name,
                '''+"'"+database_name+'''' as data_source

             
            from '''+database_name+'''.dbo.sale sale
            left join '''+database_name+'''.dbo.dm_workstation workstation
                on sale.workstation_id = workstation.workstation_id
            '''

    job_config_list = bigquery.LoadJobConfig(
        schema = [ 
                   bigquery.SchemaField("LOADED_DATE",bigquery.enums.SqlTypeNames.TIMESTAMP),
                   bigquery.SchemaField("TRAN_DATE",bigquery.enums.SqlTypeNames.TIMESTAMP),
                   bigquery.SchemaField("DATE_LAST",bigquery.enums.SqlTypeNames.TIMESTAMP),
                ]
    )

    mssql.incremental_load_sale(
                          query_string=query_string,
                          schema=schema,
                          table_id=table_name,
                          date_schema=date_schema,
                          job_config=job_config_list
                        )
    
    print('---end---')