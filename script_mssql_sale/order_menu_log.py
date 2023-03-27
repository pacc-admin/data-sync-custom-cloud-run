from google.cloud import bigquery
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import mssql

database = ['IPOSSBGN','IPOSS5WINE']
schema='IPOS_SALE'
date_schema='ORDER_DATE'

for database_name in database:
    table_name = 'order_menu_log'
    query_string = '''SELECT
                HashBytes('MD5', '''+"'"+database_name+''''+cast(pr_key as varchar)) as UNIQUE_KEY,
                *,
                getdate() as LOADED_DATE,
                '''+"'"+database_name+'''' as DATA_SOURCE

             
            from '''+database_name+'''.dbo.'''+table_name+'''
            limit 10
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
                          date_schema=date_schema,
                          job_config=job_config_list
                        )
