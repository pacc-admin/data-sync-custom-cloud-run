from big_query import connect_to_bq,bq_insert,bq_pandas
from google.cloud import bigquery
import os.path
import yaml
import time
from datetime import datetime, timedelta
import requests
import pandas as pd
import re
import inflect
import math


p = inflect.engine()

def etract_variable_yml(dictionary):
    a_yaml_file = open("credentials/base_vn_token.yml") 
    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    token=parsed_yaml_file[dictionary]
    return token

def base_vn_connect(app,component1,component2='list',updated_from=0,page=0):
    #parameter delcare
    access_token=etract_variable_yml(app)
    page_dict={'page':page}
    updated_from_dict={'updated_from':updated_from}

    #combine into dictionary
    p={**access_token,**updated_from_dict,**page_dict}

    #url specify and get data from api
    url="https://"+app+".base.vn/extapi/v1/"+component1+"/"+component2
    raw_output = requests.get(url, params=p).json()
    return raw_output

def pd_process(dataset,column_to_flat,query_string_incre,stop_words=[]):
    #flatten dataset currently nested in array column
    cp=p.plural(column_to_flat)
    dataset = pd.DataFrame(dataset)
    flatten = pd.json_normalize(dataset[cp])
    
    #Get last update date of table from BQ
    bq_table_date=bq_pandas(query_string_incre)['last_update'].astype(float).to_list()[0]
    if math.isnan(bq_table_date)==True:
        last_updated_date=0
    else:
        last_updated_date=bq_table_date

    #filter by last update date in BQ
    try:
        final_dataset = flatten[flatten['last_update'].astype('float') > last_updated_date]
    except:
        final_dataset=flatten

    #remove specified word from a list of column, for later data type change
    column_to_string = list(final_dataset.columns)
    for word in stop_words:
        column_to_string.remove(word)
    final_dataset[column_to_string]=final_dataset[column_to_string].astype(str)

    #rename schema with '.' to '_' 
    a=final_dataset.filter(like='.')
    if a.to_dict('records')==[]:
        final_dataset
    else:
        #final_dataset=flatten[flatten.columns.drop(column_to_string)].join(flatten.filter(like='.').astype(str))
        final_dataset.columns = flatten.columns.str.replace(".", "_")    

    #add loaded date field
    final_dataset['loaded_date'] = pd.to_datetime('today')

    return final_dataset
                       

def total_page(raw_output):
    try:
        r=raw_output
        total_items=int(r['total_items'])
        items_per_page=int(r['items_per_page'])
        total_page=total_items/items_per_page
    except:
        total_page=0 

    if total_page < 1:
       total_page=0
    else:
       total_page=int(round(total_page,0))
    print("Total page:",total_page)
    return total_page


def while_loop_page_insert(app,schema,column_name,query_string_incre,component2='list',job_config= bigquery.LoadJobConfig(),stop_words=[]):
    #specify variable
    client=connect_to_bq()
    pageno=-1
    r=base_vn_connect(app=app,component1=column_name,component2=component2)
    total_page_display=total_page(r)

    #loop pageno until it reach total page firgure
    while pageno < total_page_display:
        pageno=pageno+1
        r=base_vn_connect(app=app,component1=column_name,page=pageno,component2=component2)
        data_to_insert= pd_process(dataset=r,column_to_flat=column_name,query_string_incre=query_string_incre,stop_words=stop_words)
        
        if data_to_insert.to_dict('records')==[]:
            print('end')
        else:
            print('continue')
            bq_insert(client,schema,table_id=column_name,dataframe=data_to_insert,job_config=job_config)
            print('end')