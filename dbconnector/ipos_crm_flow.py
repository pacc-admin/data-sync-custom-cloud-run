from big_query import bq_insert_streaming,bq_query,bq_pandas
import requests
import pandas as pd
import time

def create_membership_table(brand):
    query_string='''
            create or replace table `pacc-raw-data.dbo._tmp_membership_check` as (
                with membership_id_sale as (
                  SELECT distinct membership_id FROM `pacc-raw-data.IPOS_SALE.sale` WHERE data_source = 'IPOSS'''+brand+''''
                ),
                
                member_vouchers as (
                  select
                      membership_id,
                      max(datetime(date_created)) as date_created
                  
                  from pacc-raw-data.IPOS_CRM_'''+brand+'''.member_vouchers
                  group by 1
                ),

                member_rating as (
                  select
                      membership_id,
                      max(datetime(created_at)) as created_at
                  
                  from pacc-raw-data.IPOS_CRM_'''+brand+'''.member_rating
                  group by 1
                )
                
                select
                    '''+"'"+brand+"'"+''' as brand,
                    membership_id_sale.membership_id,
                    coalesce(datetime(membership_details.update_at),datetime('1970-01-01')) as update_at,
                    coalesce(member_vouchers.date_created,datetime('1970-01-01')) as date_created,
                    coalesce(member_rating.created_at,datetime('1970-01-01')) as created_at
                
                from membership_id_sale
                left join pacc-raw-data.IPOS_CRM_'''+brand+'''.membership_detail membership_details
                    on membership_id_sale.membership_id = membership_details.membership_id
                left join member_vouchers
                    on member_vouchers.membership_id = membership_id_sale.membership_id
                left join member_rating
                    on member_rating.membership_id = membership_id_sale.membership_id
            )
    '''
    print(query_string)
    bq_query(query_string)

def membership_data(brand,condition=''):
    query_string='select * from `pacc-raw-data.dbo._tmp_membership_check` where brand='+"'"+brand+"'"+condition
    membership_data=bq_pandas(query_string)
    return membership_data

def crm_api(brand,user_id,table,page=0):
    p = {
      'access_token': 'ARPP3SFXSJ6R1BW5KNXEJXZV5YNENM60',
      'pos_parent':brand,
      'user_id':user_id,
      'page':page
    }
    url="https://api.foodbook.vn/ipos/ws/xpartner/"+table+"?"

    #call API
    try:
        r = requests.get(url, params=p).json()
    except:
        r=0
    
    return r
    
def crm_insert(brand,user_id,table,field_to_update,o1='',o2=''):
    r=crm_api(brand,user_id,table)
    schema='IPOS_CRM_'+brand
    table_id='pacc-raw-data.'+schema+'.'+table

    #specify updating dimension
    user_filter='and membership_id='+"'"+user_id+"'"
    updated_field=pd.to_datetime(membership_data(brand,condition=user_filter)[field_to_update]).to_list()[0]

    #convert to pandas dataframe
    if r!=0:
        try:
            a=r['data']
            if o1=='':
                object_convert=a
            else:
                print('sss')
                object_convert=a[o1]

            pandas_convert=pd.DataFrame.from_dict(object_convert)
            if pandas_convert.empty:
                dataframe=pd.DataFrame.from_dict([object_convert])
            else:
                dataframe=pandas_convert
            dataframe['membership_id']=user_id
            dataframe['loaded_date']=time.time()

            #update only changes entries
            dataframe=dataframe[pd.to_datetime(dataframe[field_to_update])>updated_field]
            if o2=='':
                dataframe=dataframe
            else:
                dataframe=dataframe[dataframe[o2]>0]
            rows_to_insert=dataframe.to_dict('records')
            print(rows_to_insert)

            #insert to BQ
            bq_insert_streaming(rows_to_insert=rows_to_insert,table_id=table_id,object='membership_id='+user_id+', brand='+brand)
            
        except:
            print('stop\n')

    else:
        print('stop\n')

def crm_insert_with_page(brand,user_id,table,field_to_update,o1='',o2=''):
    r=crm_api(brand,user_id,table)
    pageno=-1
    try:
        total_page=r['data']['totalPage']
    except:
        total_page=0

    while pageno < total_page:
        pageno=pageno+1
        crm_insert(brand,user_id,table,field_to_update,o1,o2)