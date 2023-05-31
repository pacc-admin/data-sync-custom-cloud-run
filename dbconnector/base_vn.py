from big_query import bq_insert,bq_delete
from pd_process import pd_last_update,pd_type_change
from google.cloud import bigquery
import pandas as pd
import inflect
from base_vn_api import *
import os

def base_vn_connect(app,component1,component2='list',updated_from=0,page=0,para1='',value1='',c12_plit='/'):
    if app=='hiring':
        raw_output=base_vn_connect_hiring(component1,component2=component2,updated_from=updated_from,page=page,para1=para1,value1=value1)

    elif app=='schedule':
        raw_output=get_base_schedule_api(app,component1,c12_plit=c12_plit,page=page)

    elif app=='goal':
        raw_output=get_base_goal_api(app)

    elif app=='account':
        raw_output=get_base_account(app,component1)

    else:
        raw_output=base_vn_connect_hrm_payroll(component1,app,component2=component2,updated_from=updated_from,page=page)
    return raw_output

def pd_flatten(
        raw_output,
        column_to_flat,
        url_component2='list'
    ):
    p = inflect.engine()
    #flatten dataset currently nested in array column
    
    if url_component2=='list':
        cp=p.plural(column_to_flat)
    else:
        cp=url_component2

    dataset = pd.DataFrame(raw_output)
    try:
        flatten = pd.json_normalize(dataset[cp])
    except:
        flatten = dataset
    return flatten

def pd_process(
        dataset,
        query_string_incre,
        stop_words=[]
    ):

    #filter by last update date in BQ
    final_dataset=pd_last_update(df=dataset,query_string_incre=query_string_incre)

    #rename schema with '.' to '_' 
    final_dataset.columns = [col.replace('.', '_') for col in final_dataset.columns] 

    #remove specified word from a list of column, for later data type change
    pd_type_change(df=final_dataset,columns=stop_words)

    #add loaded date field
    final_dataset['loaded_date'] = pd.to_datetime('today')
    return final_dataset
                       

def total_page(raw_output,total_items='total_items',items_per_page='items_per_page'):
    try:
        r=raw_output
        total_items=int(r[total_items])
        try:
            items_per_page=int(r[items_per_page])
        except:
            items_per_page=50
        total_page=total_items/items_per_page
    except:
        total_page=0 

    if total_page < 1:
       total_page=0
    else:
       total_page=int(round(total_page,0))
    print("Total page:",total_page)
    return total_page

def single_page_insert(app,
                       schema,
                       table,
                       query_string_incre,
                       component1='',
                       stop_words=[],
                       job_config= bigquery.LoadJobConfig()
                    ):
    
    raw_output=base_vn_connect(app,component1=component1)
    dataset=pd.DataFrame(raw_output)

    data_to_insert= pd_process(
                                dataset,
                                query_string_incre,
                                stop_words=stop_words
                            )
    #condition to exclude
    try:
        condition='id in '+"('"+"','".join(data_to_insert['id'].to_list())+"')"
    except:
        condition='true'
    

    #insert to BQ
    result=bq_insert(
                schema,
                table_id=table,
                dataframe=data_to_insert,
                condition=condition,
                job_config=job_config,
                unique_key='id'
            )
    print(result)


def while_loop_page_insert(app,
                           schema,
                           column_name,
                           query_string_incre,
                           component2='list',
                           para1='',
                           value1='',
                           c12_plit='/',
                           job_config= bigquery.LoadJobConfig(),
                           stop_words=[],
                           total_items='total_items',
                           items_per_page='items_per_page'
                        ):
    #specify variable
    pageno=-1
    r=base_vn_connect(app=app,component1=column_name,component2=component2,para1=para1,value1=value1,c12_plit=c12_plit)
    if r['message'] !='':
        print('URL error, stop')
    else:
        total_page_display=total_page(r,total_items,items_per_page)
        
        #regulate table name from components
        if component2=='list':
            table_id=column_name
        else:
            table_id=column_name+'_'+component2
        
        if total_page_display<=1:
            dataset=pd_flatten(raw_output=r,column_to_flat=column_name,url_component2=component2)
    
        else:
            dataset=pd.DataFrame()
    
            print('start loop')
            while pageno < total_page_display:
                pageno=pageno+1
                print(pageno)
                r=base_vn_connect(app=app,component1=column_name,page=pageno,component2=component2,para1=para1,value1=value1,c12_plit=c12_plit)
                dataset_raw=pd_flatten(raw_output=r,column_to_flat=column_name,url_component2='list')
                dataset=pd.concat([dataset,dataset_raw])
       
        data_to_insert= pd_process(
                                    dataset,
                                    query_string_incre,
                                    stop_words=stop_words
                                )
        #condition to exclude
        try:
            condition='id in '+"('"+"','".join(data_to_insert['id'].to_list())+"')"
        except:
            condition='true'
    
        #insert to BQ
        result=bq_insert(
                    schema,
                    table_id=table_id,
                    dataframe=data_to_insert,
                    condition=condition,
                    job_config=job_config,
                    unique_key='id'
                )
        print(result)
    
        