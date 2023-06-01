import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query

brand='BGN'
#schema='IPOS_CRM_'+brand
schema='dbo'
#table='member_vouchers'
table='membership_detail'
field_to_update='update_at'
columns_to_preserve=['gender',
                    'address',
                    'point',
                    'payment_amount',
                    'point_amount',
                    'eat_times',
                    'is_zalo_follow',
                    'age',
                    'phone_number'
                ]

ipos_crm_flow.crm_insert(brand,table,field_to_update,columns_to_preserve)