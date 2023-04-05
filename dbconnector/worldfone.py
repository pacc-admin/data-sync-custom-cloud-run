import requests
import time
import pandas as pd
from datetime import datetime
from big_query import bq_insert
from yml_extract import etract_variable_yml_string
from time_function import last_unix_t_of_month


def get_worldfone_api(startdate,enddate,page=1):
    worldfone_key=etract_variable_yml_string(dictionary_1='worldfone',dictionary_2='secret_key',file_name='worldfone_key')
    url='https://apps.worldfone.vn/externalcrm/getcdrs.php?secret='+str(worldfone_key)+'&startdate='+str(startdate)+'&enddate='+str(enddate)+'&page='+str(page)+'&pageSize=100'
    print(url)
    raw_output = requests.post(url).json()
    
    return raw_output

def worldfone_pd(start_date,end_date):

    #getting total pages
    data_to_insert=pd.DataFrame()
    raw_output = get_worldfone_api(startdate=start_date,enddate=end_date)
    total_pages=raw_output['max_page']+1
    print(total_pages)

    #concat df to all pages data
    for page in range(1,total_pages):
        raw_output = get_worldfone_api(startdate=start_date,enddate=end_date,page=page)
        df=pd.DataFrame(raw_output['data'])
        data_to_insert=pd.concat([data_to_insert,df])
        data_to_insert['loaded_date'] = pd.to_datetime('today')
    
    return data_to_insert

def worldfone_bq(start_date,end_date,schema,table_id):
    data_to_insert=worldfone_pd(start_date,end_date)

    if data_to_insert.to_dict('records')==[]:
        result='No Insert'
        print('end')
        
    else:
        print('continue')

        result=bq_insert(
                    schema,
                    table_id,
                    dataframe=data_to_insert
                )
        print('end')

    print(result)
    return result

def worldfone_bq_historical(schema,table_id):
    today_unix = int(time.mktime(datetime.today().timetuple()))
    start_date=1614531599
    end_date=1614531600
    order=0
    while start_date <= today_unix:
        order=order+1
        print(order)
        start_date=end_date+1
        print('first timestamp of month is: '+str(start_date))
        end_date=last_unix_t_of_month(start_date)
        
        worldfone_bq(start_date=start_date,end_date=end_date,schema=schema,table_id=table_id)
        print(' ')