from google.cloud import bigquery
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import big_query
import mssql

database = ['IPOSSBGN','IPOSS5WINE']
schema='IPOS_SALE'
date_schema='ORDER_DATE'
date_to_delete= 30
table_names = ['order_menu_log_bgn','order_menu_log_5wine']

condition = "date_diff(current_date,date("+date_schema+"),day) <="+str(date_to_delete)

for database_name,table_name in zip(database,table_names):
    print('---start---')
    print('Loaded from MSSQL:'+database_name+' to BQ:'+table_name)
    big_query.bq_delete(schema,table_name,condition=condition)
    query_string = '''SELECT
                HashBytes('MD5', '''+"'"+database_name+''''+cast(pr_key as varchar)) as UNIQUE_KEY,
                *,
                '''+"'"+database_name+'''' as DATA_SOURCE

             
            from '''+database_name+'''.dbo.'''+table_name+'''
            '''

    job_config_list = bigquery.LoadJobConfig(
        schema = [ 
                   bigquery.SchemaField("LOADED_DATE",bigquery.enums.SqlTypeNames.TIMESTAMP),
                   bigquery.SchemaField("ORDER_DATE",bigquery.enums.SqlTypeNames.DATETIME),
                   bigquery.SchemaField("SERVICE_DATE",bigquery.enums.SqlTypeNames.DATETIME),
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