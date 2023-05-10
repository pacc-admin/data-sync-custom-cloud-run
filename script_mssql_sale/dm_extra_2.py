
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import mssql,big_query

database = ['IPOSS5WINE','IPOSSBGN']
schema='IPOS_SALE'
table_name='dm_extra_2'

for database_name in database:
    condition="data_source='"+database_name+"'"
    query_string = "select *, "+"'"+database_name+"'"+' as data_source from '+database_name+'.dbo.'+table_name
    mssql.full_refresh_sale(query_string,schema,table_name,condition=condition)
