from big_query import bq_insert,bq_delete,bq_pandas
from google.cloud import bigquery
import yaml
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

def base_vn_connect(app,component1,component2='list',updated_from=0,page=0,para1='',value1='',para2='',value2=''):
    #parameter delcare
    access_token=etract_variable_yml(app)
    page_dict={'page':page}
    updated_from_dict={'updated_from':updated_from}
    h = {"Content-type": "application/x-www-form-urlencoded"}
    print(para2)

    #combine into dictionary
    if para1=='' and para2=='':
        p={**access_token,**updated_from_dict,**page_dict}
    elif para1!='' and para2=='':
        p={**access_token,**updated_from_dict,**page_dict,**{para1:value1}}
    elif para2!='' and para1=='':
        p={**access_token,**updated_from_dict,**page_dict,**{para2:value2}}
    else:
        p={**access_token,**updated_from_dict,**page_dict,**{para1:value1},**{para2:value2}}
    
    print(p)
    if component2 !='':
        try:
            url="https://"+app+".base.vn/extapi/v1/"+component1+"/"+component2
            tester=requests.get(url, params=p).json()
            if tester['data']=='':
                raw_output = tester
            else:
                url="https://"+app+".base.vn/publicapi/v2/"+component1+"/"+component2
                raw_output = requests.post(url, headers=h, data=p).json()            
        except:
            url="https://"+app+".base.vn/publicapi/v2/"+component1+"/"+component2
            raw_output = requests.post(url, headers=h, data=p).json()
    else:
        url="https://"+app+".base.vn/extapi/v1/"+component1
        print(url)
        raw_output = requests.post(url, headers=h, data=p).json()
    return raw_output

import ast
def pd_process(
        raw_output,
        column_to_flat,
        query_string_incre,
        stop_words=[],
        url_component2='list'
    ):
    #flatten dataset currently nested in array column
    if url_component2=='list':
        cp=p.plural(column_to_flat)
    else:
        cp=url_component2
    dataset = pd.DataFrame(raw_output)
    flatten = pd.json_normalize(dataset[cp])
    
    #Get last update date of table from BQ
    try:
        bq_table_date=bq_pandas(query_string_incre)['last_update'].astype(float).to_list()[0]
        if math.isnan(bq_table_date)==True:
            last_updated_date=0
        else:
            last_updated_date=bq_table_date
    except:
        last_updated_date=0


    #filter by last update date in BQ
    try:
        final_dataset = flatten[flatten['last_update'].astype('float') > last_updated_date]
    except:
        final_dataset=flatten

    #rename schema with '.' to '_' 
    a=final_dataset.filter(like='.')
    final_dataset.columns = final_dataset.columns.str.replace(".", "_", regex=True) 

    #remove specified word from a list of column, for later data type change
    column_to_string = list(final_dataset.columns)
    if stop_words==[]:
        final_dataset[column_to_string]=final_dataset[column_to_string].astype(str)
    else:
        for word in stop_words:
            column_to_string.remove(word)
        final_dataset[column_to_string]=final_dataset[column_to_string].astype(str)
        final_dataset.apply(pd.Series)

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


def while_loop_page_insert(app,
                           schema,
                           column_name,
                           query_string_incre,
                           component2='list',
                           para1='',
                           value1='',
                           job_config= bigquery.LoadJobConfig(),
                           stop_words=[]
                        ):
    #specify variable
    pageno=-1
    r=base_vn_connect(app=app,component1=column_name,component2=component2,para1=para1,value1=value1)
    total_page_display=total_page(r)

    #regulate table name from components
    if component2=='list':
        table_id=column_name
    else:
        table_id=column_name+'_'+component2

    #loop pageno until it reach total page firgure
    while pageno < total_page_display:
        pageno=pageno+1
        r=base_vn_connect(app=app,component1=column_name,page=pageno,component2=component2,para1=para1,value1=value1)
        try:    
            data_to_insert= pd_process(
                                    raw_output=r,
                                    column_to_flat=column_name,
                                    query_string_incre=query_string_incre,
                                    stop_words=stop_words,
                                    url_component2=component2
                            )
    
            #stop if inserted objects is empty
            if data_to_insert.to_dict('records')==[]:
                print('end')
            else:
                print('continue')
    
                #remove column with id matches the inserted rows from basevn
                print(data_to_insert['id'])
                row_to_exclude="('"+"','".join(data_to_insert['id'].to_list())+"')"
                condition='id in'+row_to_exclude
                bq_delete(schema,table_id,condition=condition)
    
                bq_insert(
                    schema,
                    table_id=table_id,
                    dataframe=data_to_insert,
                    job_config=job_config
                )
                print('end')
        except:
            print('end')