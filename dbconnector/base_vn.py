from big_query import bq_insert,bq_delete
from pd_process import pd_last_update,pd_type_change
from google.cloud import bigquery
import pandas as pd
import inflect
from base_vn_api import base_vn_connect_hiring,base_vn_connect_hrm_payroll
import os

def base_vn_connect(app,component1,component2='list',updated_from=0,page=0,para1='',value1=''):
    if app=='hiring':
        raw_output=base_vn_connect_hiring(component1,component2=component2,updated_from=updated_from,page=page,para1=para1,value1=value1)
    
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
    flatten = pd.json_normalize(dataset[cp])
    return flatten

def pd_process(
        dataset,
        query_string_incre,
        stop_words=[]
    ):

    #filter by last update date in BQ
    final_dataset=pd_last_update(df=dataset,query_string_incre=query_string_incre)

    #rename schema with '.' to '_' 
    final_dataset.columns = final_dataset.columns.str.replace(".", "_", regex=True) 

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


def while_loop_page_insert(app,
                           schema,
                           column_name,
                           query_string_incre,
                           component2='list',
                           para1='',
                           value1='',
                           job_config= bigquery.LoadJobConfig(),
                           stop_words=[],
                           total_items='total_items',
                           items_per_page='items_per_page'
                        ):
    #specify variable
    pageno=-1
    r=base_vn_connect(app=app,component1=column_name,component2=component2,para1=para1,value1=value1)
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
            r=base_vn_connect(app=app,component1=column_name,page=pageno,component2=component2,para1=para1,value1=value1)
            dataset_raw=pd_flatten(raw_output=r,column_to_flat=column_name,url_component2='list')
            dataset=pd.concat([dataset,dataset_raw])
       
    data_to_insert= pd_process(
                                dataset,
                                query_string_incre,
                                stop_words=stop_words
                            )
    #stop if inserted objects is empty
    if data_to_insert.to_dict('records')==[]:
        result='No Insert'
        print('end')
        
    else:
        print('continue')
        #remove column with id matches the inserted rows from basevn
        row_to_exclude="('"+"','".join(data_to_insert['id'].to_list())+"')"
        condition='id in'+row_to_exclude
        bq_delete(schema,table_id,condition=condition)

        result=bq_insert(
                    schema,
                    table_id=table_id,
                    dataframe=data_to_insert,
                    job_config=job_config
                )
        print('end')
    print(result)
    return result
    
        