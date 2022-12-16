import yaml
import time
from datetime import datetime, timedelta
import requests
import re

def etract_variable_yml(dictionary):
    a_yaml_file = open("credentials/base_vn_token.yml")
    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    token=parsed_yaml_file[dictionary]
    return token

def base_vn_connect(app,component1,component2='list',updated_from=0,page=0):
    samp= re.compile('[a-zA-z]+')
    component1=samp.findall(component1)[0]
    component2=samp.findall(component2)[0]
    access_token = etract_variable_yml(app)
    page_dict={'page':page}
    updated_from_dict={'updated_from':updated_from}
    p={**access_token,**updated_from_dict,**page_dict}
    print(p)
    url="https://"+app+".base.vn/extapi/v1/"+component1+"/"+component2
    print(url)
    raw_output = requests.get(url, params=p).json()
    return raw_output

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
