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
def get_cycles(access_token):
    print('get path')
    url='https://goal.base.vn/extapi/v1/cycle/list'

    raw_output=requests.post(url,data=access_token).json()['cycles']
    return raw_output


def get_goal_id(access_token):
    print('get goal id')
    cycles_paths=[]
    cycles_response=get_cycles(access_token)
    for d in cycles_response:
        cycles_paths.append(d['path'])
    print('cycles_paths is '+str(cycles_paths))

    goal_ids=[]
    for path in cycles_paths:
        goal_id_cycles=[]
        d={**access_token,**{'path':path}}
        url='https://goal.base.vn/extapi/v1/cycle/get.full'
        response=requests.post(url,data=d).json()
        
        for d in response['goals']:
            goal_id_cycles.append(d['id'])
        goal_ids=goal_ids+goal_id_cycles
        
    print('goal id list is '+str(goal_ids))
    return goal_ids

def get_base_goal_api(app):
    access_token=etract_variable_yml_dict(app)
    goal_ids=get_goal_id(access_token)
    goal_detail=[]
    for goal_id in goal_ids:
        print('goal detail extract for goal id '+str(goal_id))
        d={**access_token,**{'id':goal_id}}
        url='https://goal.base.vn/extapi/v1/goal/get'
    
        response=requests.post(url,data=d).json()
        goal_detail_response=response['goal']
        goal_detail.append(goal_detail_response)
    
    print('finish getting raw output')
    return goal_detail