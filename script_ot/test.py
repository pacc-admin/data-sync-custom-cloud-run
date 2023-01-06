import requests
import json 
import pandas as pd
import sys, os
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query


brand='BGN'

df = ipos_crm_flow.membership_data(brand)
user_id_list=df['membership_id'].to_list()
#user_id_list=['84896499194']
for user_id in user_id_list:
    print('start with member_id:'+user_id)
    table = 'member_rating'

    field_to_update='created_at'
    print('insert table '+table)
    ipos_crm_flow.crm_insert_with_page(brand,user_id,table,field_to_update,o1='rates',o2='score')
    
    
    