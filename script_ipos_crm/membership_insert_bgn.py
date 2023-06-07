import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query,dict_function

brand='BGN'
schema='IPOS_CRM_'+brand
table='membership_detail'
column_updated='update_at'

#execute
source_output=ipos_crm_flow.crm_get_full_list(brand,table)
big_query.full_refresh_bq_insert_from_json(source_output,schema,table_id=table)