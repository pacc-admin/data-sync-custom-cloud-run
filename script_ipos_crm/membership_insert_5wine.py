import requests
import json 
import pandas as pd
import sys, os
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import mssql,big_query

brand='5WINE'
dataframe = mssql.mssql_query_pd_sale(query_string='select distinct membership_id from IPOSS5WINE.dbo.sale where len(membership_id)>10')
#user_id_list=dataframe['membership_id'].to_list()
user_id_list=['841687996355']
table_id_template = 'pacc-raw-data.IPOS_CRM_'+brand+'.'

for user_id in user_id_list:
    print(user_id)
    p = {
      'access_token': 'ARPP3SFXSJ6R1BW5KNXEJXZV5YNENM60',
      'pos_parent':brand,
      'user_id':user_id
    }

    #membership_detail
    table='membership_detail'
    table_id=table_id_template+table+'s'

    try:
        url="https://api.foodbook.vn/ipos/ws/xpartner/"+table+"?"
        r = requests.get(url, params=p).json()
    except:
        r=0
    
    if r!=0:
        try:
            a=r['data']
            dataframe=pd.DataFrame.from_dict([a])
            dataframe['membership_id']=user_id
            dataframe['loaded_date']=time.time()
            rows_to_insert=dataframe.to_dict('records')
            print(rows_to_insert)
            big_query.bq_insert_streaming(rows_to_insert=rows_to_insert,table_id=table_id,object='membership_id='+user_id+', brand='+brand)
        except:
            print('stop')

    else:
        print('stop')
    
    #membership_voucher
    table='member_voucher'
    table_id=table_id_template+table+'s'
    url="https://api.foodbook.vn/ipos/ws/xpartner/"+table+"?"
    try:
        r = requests.get(url, params=p).json()
    except:
        r=0
    
    if r!=0:
        try:
            a=r['data']
            dataframe=pd.DataFrame(a).astype(str)
            dataframe['membership_id']=user_id
            dataframe['loaded_date']=time.time()
            rows_to_insert=dataframe.to_dict('records')
            print(rows_to_insert)
            big_query.bq_insert_streaming(rows_to_insert=rows_to_insert,table_id=table_id,object='membership_id='+user_id+', brand='+brand)
        except:
            print('stop')

    else:
        print('stop')