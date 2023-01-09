import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query

brand='BGN'
ipos_crm_flow.create_membership_table(brand)
df = ipos_crm_flow.membership_data(brand)
user_id_list=df['membership_id'].to_list()

for user_id in user_id_list:
    print('start with member_id:'+user_id)
    
    table='membership_detail'
    print('insert table '+table)
    field_to_update='update_at'
    ipos_crm_flow.crm_insert(brand,user_id,table,field_to_update)

    table='member_vouchers'
    print('insert table '+table)
    field_to_update='date_created'
    ipos_crm_flow.crm_insert(brand,user_id,table,field_to_update)

    table = 'member_rating'
    print('insert table '+table)
    field_to_update='created_at'
    print('insert table '+table)
    ipos_crm_flow.crm_insert_with_page(brand,user_id,table,field_to_update,o1='rates',o2='score')

big_query.bq_query(query_string='drop table `pacc-raw-data.dbo._tmp_membership_check`')