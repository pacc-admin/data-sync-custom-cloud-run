import sys, os
import pandas as pd
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query

brand='BGN'
schema='dbo'
table='member_vouchers'
field_to_update='update_at'

df = ipos_crm_flow.membership_data(brand)
user_id_list=df['membership_id'].to_list()
print(user_id_list)
