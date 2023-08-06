from big_query import bq_insert_streaming,bq_query,bq_pandas,bq_insert,bq_delete
from mssql import mssql_query_pd
from pd_process import pd_last_update,pd_type_change
from dict_function import incremental_dict
from google.cloud import bigquery
import requests
import pandas as pd
import datetime

def membership_data(brand,condition=''):
    database_name='IPOSS'+brand
    query_string='select distinct '+condition+' membership_id from '+database_name+'.dbo.sale'
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
        r = requests.get(url, params=p).json()['data']
    except:
        print('error')
        r=0
    
    return r

def crm_get_full_list(brand,table,page=0):
    #df = membership_data(brand)
    #user_id_list=df['membership_id'].to_list()
    user_id_list=['84903003380','84907090991','84968757511','84982050271','84909151071','84973382047','84901632068','84907090991']
    
    raw_output=[]
    for user_id in user_id_list:
        print('get data for member_id:'+user_id)
        raw_output_member=crm_api(brand,user_id,table,page=0)

        if raw_output_member==0 or raw_output_member==[]:
            print('no data')
        else:
            try:
                updated_data = raw_output_member.copy()
                updated_data['membership_id']=user_id

            except:
                updated_data = []
                for row in raw_output_member:
                    updated_dictionary = row.copy()
                    updated_dictionary['membership_id']=user_id
                    updated_data.append(updated_dictionary)

            if type(raw_output_member) is dict:
                raw_output.append(updated_data)
            else:
                raw_output=raw_output+updated_data   

        for raw_output_dict in raw_output:
            raw_output_dict['loaded_date']=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f') + ' UTC'

    return raw_output
    
def crm_transform(raw_output,user_id,schema,table,field_to_update,columns_to_preserve=[]):
    #specify updating dimension
    query_string_incre='select max(unix_seconds(timestamp('+field_to_update+'))) as '+field_to_update+'''
                           from `pacc-raw-data.'''+schema+'''.'''+table+'`'

    #convert to df
    dataframe=pd.DataFrame(raw_output)

    #update only changes entries
    print('start update')
    dataframe=pd_last_update(dataframe,query_string_incre,field_to_update)

    #change type
    dataframe=pd_type_change(dataframe,columns=columns_to_preserve)  

    #adding column
    dataframe['membership_id']=user_id
    dataframe['loaded_date'] = pd.to_datetime('today')

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

def crm_insert(brand,table,field_to_update,columns_to_preserve=[],unique_id=''):
    #schema='IPOS_CRM_'+brand
    schema='dbo'    
    print('insert table '+table)
    
    source_output=dict_function.incremental_dict(raw_output,column_updated,schema,table)    
    dataframe=crm_transform(raw_output,user_id,schema,table,field_to_update,columns_to_preserve)
    #try:
    #    dataframe=dataframe[dataframe[unique_id].notnull()]
    #except:
    #    dataframe=dataframe
    
    print(dataframe)
    job_config_list = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("loaded_date",bigquery.enums.SqlTypeNames.TIMESTAMP)
            ]
    )

    #recreate the sql file
    print('recreate the sql file')
    file_path='.SQL_create_table/ipos_crm/'+table+'.sql'
    fd = open(file_path, 'r')
    query_string ='create or replace table `pacc-raw-data.'+schema+'.'+table+'` '+fd.read()
    #print(query_string)

    #bq_query(query_string)
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
