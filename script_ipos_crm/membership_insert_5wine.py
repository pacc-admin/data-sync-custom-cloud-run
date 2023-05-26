import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow

brand='5WINE'
schema='IPOS_CRM_'+brand
#table='member_vouchers'
table='membership_detail'
field_to_update='update_at'

ipos_crm_flow.crm_insert(brand,table,field_to_update)