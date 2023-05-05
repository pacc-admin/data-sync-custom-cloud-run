import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow

brand='5WINE'
table='member_vouchers'
field_to_update='update_at'

ipos_crm_flow.crm_insert(brand,table,field_to_update)