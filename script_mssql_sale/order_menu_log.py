from google.cloud import bigquery
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import big_query
import mssql

database = ['IPOSSBGN','IPOSS5WINE']
schema='IPOS_SALE'
date_schema='ORDER_DATE'
table_name = 'order_menu_log'
date_to_delete=30

condition = "date_diff(current_date,date(tran_date),day) <="+str(date_to_delete)
big_query.bq_delete(schema,table_name,condition=condition)

for database_name in database:
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
                          mssql_database_name=database_name,
                          schema=schema,
                          table_id=table_name,
                          condition_loaded_date="data_source = '"+database_name+"'",                           
                          date_schema=date_schema,
                          job_config=job_config_list
                        )
