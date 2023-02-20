import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
from mssql_dedup import mssql_bq_dedup

mssql_databases = ['IACC_BGPACC2022','IACC_BGPACCBAUCAT2022']
bq_schemas = ['IPOS_ACCOUNTING','IPOS_ACCOUNTING_BAUCAT']

for (mssql_database,bq_schema) in zip(mssql_databases,bq_schemas):
    print(mssql_database)
    print(bq_schema)
    with mssql_bq_dedup( unique_id='pr_key_ledger',
                     branch_schema='job_id',
                     mssql_table='ledger',
                     mssql_database=mssql_database,
                     bq_schema=bq_schema,
                     bq_table_id_dedup='ledger_dedup',
                     bq_table_id='ledgers_analytics'

    ) as s:
        s.connect_to_mssql()
        s.mssql_query_pd()
        s.bq_delete_insert_warehouse_dedup()
        s.bq_dedup_warehouse()