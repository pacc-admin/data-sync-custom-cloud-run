import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query

brand='BGN'
schema='IPOS_CRM_'+brand
table='member_vouchers'
field_to_update='update_at'

big_query.bq_delete(schema,table,condition='true')
ipos_crm_flow.crm_insert(brand,table,field_to_update)