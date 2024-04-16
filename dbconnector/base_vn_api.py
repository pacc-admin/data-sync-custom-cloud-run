import requests
from datetime import datetime
from big_query import bq_pandas
from yml_extract import etract_variable_yml_dict
from time_function import last_unix_t_of_month,first_unix_t_of_last_month

import time

def base_vn_connect_hiring(component1,app='hiring',component2='list',updated_from=0,page=0,para1='',value1=''):
    #parameter delcare
    access_token=etract_variable_yml_dict(app)
    page_dict={'page':page}
    updated_from_dict={'updated_from':updated_from}
    h = {"Content-type": "application/x-www-form-urlencoded"}

    #combine into dictionary
    if para1=='':
        p={**access_token,**updated_from_dict,**page_dict}
    else:
        p={**access_token,**updated_from_dict,**page_dict,**{para1:value1}}
        
    url="https://"+app+".base.vn/publicapi/v2/"+component1+"/"+component2
    raw_output = requests.post(url, headers=h, data=p).json()
    
    return raw_output


def base_vn_connect_hrm_payroll(component1,app,component2='list',updated_from=0,page=0):
    #parameter delcare
    access_token=etract_variable_yml_dict(app)
    page_dict={'page':page}
    updated_from_dict={'updated_from':updated_from}

    #combine into dictionary
    p={**access_token,**updated_from_dict,**page_dict}

    url="https://"+app+".base.vn/extapi/v1/"+component1+"/"+component2
    raw_output = requests.post(url, data=p).json()
    
    return raw_output


def get_base_checkin_api(query_string,app='checkin'):
    latest_date_bq=bq_pandas(query_string)['logs_time'].astype(int).to_list()[0] + 1
    print('latest timestamp on checkin logs is: '+str(latest_date_bq))

    #parameter delcare
    component1='getlogs'
    app='checkin'
    start_date=latest_date_bq
    access_token=etract_variable_yml_dict(app)
    today_unix = int(time.mktime(datetime.today().timetuple()))
    date_1=start_date,
    date_2=today_unix,  
    
    h = {"Content-type": "application/x-www-form-urlencoded"}
    p={**access_token,**{'start_date':date_1},**{'end_date':date_2}}
    url="https://"+app+".base.vn/extapi/v1/"+component1
    
    raw_output = requests.post(url, headers=h, data=p).json()
    
    return raw_output

def get_base_schedule_api(app,component1,c12_plit='/',page=0):

    #parameter delcare
    component2='list'
    page_dict={'page':page}
    access_token=etract_variable_yml_dict(app)
    
    today_unix = int(time.mktime(datetime.today().timetuple()))
    date_1=first_unix_t_of_last_month(today_unix)
    date_2=last_unix_t_of_month(today_unix)
    
    h = {"Content-type": "application/x-www-form-urlencoded"}
    p={**access_token,**{'start_time':date_1},**{'end_time':date_2},**page_dict}
    url="https://"+app+".base.vn/extapi/v1/"+component1+c12_plit+component2
    raw_output = requests.post(url, headers=h, data=p).json()
    
    return raw_output

###base account
def get_base_account(app,component1):
    access_token=etract_variable_yml_dict(app)
    url='https://account.base.vn/extapi/v1/'+component1
    raw_output=requests.post(url,data=access_token).json()[component1]
    return raw_output

###base goal
def get_cycles(app):
    print('get path')
    access_token=etract_variable_yml_dict(app)
    url='https://goal.base.vn/extapi/v1/cycle/list'

    raw_output=requests.post(url,data=access_token).json()['cycles']
    return raw_output


def get_metric_id(app,metric):
    print('get '+metric+' id')
    access_token=etract_variable_yml_dict(app)
    cycles_paths=[]
    cycles_response=get_cycles(app)

    metric_id_cycles=[]
    metric_object=metric+'s'

    for d in cycles_response:
        cycles_paths.append(d['path'])
    print('cycles_paths is '+str(cycles_paths))

    for path in cycles_paths:
        d={**access_token,**{'path':path}}
        url='https://goal.base.vn/extapi/v1/cycle/get.full'
        response=requests.post(url,data=d).json()

        for metric_list in response[metric_object]:
            metric_id_cycles.append(metric_list['id'])
        
    print(metric+' id list is '+str(metric_id_cycles))
    return metric_id_cycles

def get_base_goal_metric_api(app,metric):
    access_token=etract_variable_yml_dict(app)
    metric_ids=get_metric_id(app,metric)
    metric_detail=[]

    for metric_id in metric_ids:
        print(metric+' detail extract for '+metric+' id '+str(metric_id))
        d={**access_token,**{'id':metric_id}}
        url='https://goal.base.vn/extapi/v1/'+metric+'/get'
    
        response=requests.post(url,data=d).json()
        metric_detail_response=response[metric]
        metric_detail.append(metric_detail_response)
    
    print('finish getting raw output')
    return metric_detail



def get_total_page(raw_output,total_items='total_items',items_per_page='items_per_page'):
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

#base timeoff
def get_base_timeoff():
    access_token=etract_variable_yml_dict('timeoff')
    h = {"Content-type": "application/x-www-form-urlencoded"}
    page_dict={'page':0}
    p={**access_token,**page_dict}
    url = 'https://timeoff.base.vn/extapi/v1/timeoff/list'
    raw_output = requests.post(url, headers=h, data=p).json()

    #total_page = get_total_page(raw_output)
    total_page = 30
    final_output = []

    for page in range(0,total_page + 1):
        print(page)
        page_dict={'page':page}
        p={**access_token,**page_dict}
        final_output_raw = requests.post(url, headers=h, data=p).json()
        final_output_page = final_output_raw['timeoffs']    
        final_output = final_output + final_output_page
    
    return final_output