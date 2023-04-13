import requests
from datetime import datetime
from big_query import bq_pandas
from yml_extract import etract_variable_yml_dict
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
    date_1=1672506000
    date_2=today_unix
    
    h = {"Content-type": "application/x-www-form-urlencoded"}
    p={**access_token,**{'start_time':date_1},**{'end_time':date_2},**page_dict}
    url="https://"+app+".base.vn/extapi/v1/"+component1+c12_plit+component2
    raw_output = requests.post(url, headers=h, data=p).json()
    
    return raw_output