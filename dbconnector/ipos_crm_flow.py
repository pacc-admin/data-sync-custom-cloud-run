from big_query import bq_insert_streaming,bq_query,bq_pandas,bq_insert,bq_delete
from mssql import mssql_query_pd
from pd_process import pd_last_update,pd_type_change
from google.cloud import bigquery
import requests
import pandas as pd
import time

def membership_data(brand,condition=''):
    database_name='IPOSS'+brand
    query_string='select '+condition+' distinct membership_id from '+database_name+'.dbo.sale'
    membership_data=mssql_query_pd(query_string)
    print('Total members are '+str(len(membership_data.index)))
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
    
def crm_transform(brand,user_id,schema,table,field_to_update,columns_to_convert=[],o1='',o2=''):
    r=crm_api(brand,user_id,table)

    #specify updating dimension
    user_filter='and membership_id='+"'"+user_id+"'"
    query_string_incre='select max(unix_seconds(timestamp('+field_to_update+'))) as '+field_to_update+'''
                           from `pacc-raw-data.'''+schema+'''.'''+table+'` where membership_id='+"'"+user_id+"'"
    
    #convert to pandas dataframe
    if r!=0:
        try:
            a=r['data']
            if o1=='':
                object_convert=a
            else:
                object_convert=a[o1]

            pandas_convert=pd.DataFrame.from_dict(object_convert)
            if pandas_convert.empty:
                dataframe=pd.DataFrame.from_dict([object_convert])
            else:
                dataframe=pandas_convert

            if dataframe.empty:
                print('empty dataframe')
            
            else:
                #update only changes entries
                print('start update')
                dataframe=pd_last_update(dataframe,query_string_incre,field_to_update)

                #adding column
                dataframe['membership_id']=user_id
                dataframe['loaded_date'] = pd.to_datetime('today')

                #change type
                dataframe=pd_type_change(dataframe,columns=columns_to_convert,type='include')

            if o2=='':
                dataframe=dataframe
            else:
                dataframe=dataframe[dataframe[o2]>0]
            
        except:
            dataframe=pd.DataFrame()

    else:
        dataframe=pd.DataFrame()
    print(dataframe)    
    return dataframe

def crm_insert_with_page(brand,user_id,table,field_to_update,o1='',o2=''):
    r=crm_api(brand,user_id,table)
    pageno=-1
    try:
        total_page=r['data']['totalPage']
    except:
        total_page=0

    while pageno < total_page:
        pageno=pageno+1
        crm_transform(brand,user_id,table,field_to_update,o1,o2)

def crm_insert(brand,table,field_to_update,columns_to_convert=[],unique_id='voucher_code'):
    df = membership_data(brand)
    user_id_list=df['membership_id'].to_list()
    schema='IPOS_CRM_'+brand
    print(schema)
    
    print('insert table '+table)
    
    dataframe=pd.DataFrame()
    for user_id in user_id_list:
        print('start with member_id:'+user_id)
        dataframe_user_id=crm_transform(brand,user_id,schema,table,field_to_update,columns_to_convert=columns_to_convert)
        dataframe=pd.concat([dataframe,dataframe_user_id])
    
    try:
        dataframe=dataframe[dataframe[unique_id].notnull()]
    except:
        dataframe=dataframe
        
    print(dataframe)
    job_config_list = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)
            ]
    )

    #recreate the sql file
    print('recreate the sql file')
    file_path='.SQL_create_table/basevn/hrm/'+table+'.sql'
    fd = open(file_path, 'r')
    sqlFile = fd.read()
    print(sqlFile)

    bq_query(query_string)
    fd.close()

    #insert data to BQ
    bq_insert(schema,table,dataframe,job_config=job_config_list)


def crm_campaigns_insert(brand):
    #variable
    access_token='ARPP3SFXSJ6R1BW5KNXEJXZV5YNENM60'
    url='https://api.foodbook.vn/ipos/ws/xpartner/campaigns?access_token='+access_token+'&pos_parent='+brand
    component='campaigns'
    schema='IPOS_CRM_'+brand
    table_id=component
    column_updated='date_updated_unix'
    query_string_incre='select max('+column_updated+') as '+column_updated+' from `pacc-raw-data.'+schema+'.'+component+'`'
    
    #get api
    output=requests.get(url).json()
    data=output['data']
    df=pd.DataFrame(data[component])

    #column add
    df['date_updated_unix']=pd.to_datetime(df['date_updated']).map(pd.Timestamp.timestamp)
    df['loaded_date'] = pd.to_datetime('today')

    #last update data only
    dataframe=pd_last_update(df,query_string_incre,column_updated)

    #bq_insert
    bq_insert(schema,table_id,dataframe)
