import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query,dict_function

brand='5WINE'
schema='IPOS_CRM_'+brand
table='member_vouchers'

#execute
source_output=ipos_crm_flow.crm_get_full_list(brand,table)
#source_output=dict_function.incremental_dict(raw_output,column_updated,schema,table,column_type='datetime')
big_query.full_refresh_bq_insert_from_json(source_output,schema,table_id=table)