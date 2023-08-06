import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query,dict_function

brand='BGN'
schema='IPOS_CRM_'+brand
table='member_vouchers'

#execute
source_output=ipos_crm_flow.crm_get_full_list(brand,table)
try:
    big_query.full_refresh_bq_insert_from_json(source_output,schema,table_id=table)
except:
    query_string = 'create or replace table '+schema+'.'+table+' (loaded_date timestamp)'
    big_query.bq_query(query_string)
    big_query.full_refresh_bq_insert_from_json(source_output,schema,table_id=table)
