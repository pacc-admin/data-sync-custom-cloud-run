import requests
import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

import big_query

#url='https://goal.base.vn/extapi/v1/checkin/kr'
url='https://goal.base.vn/extapi/v1/checkin/goal.kpi'
access_token={'access_token':'7383-QRDX8A6GJKSU9ZW9B6F75FEYRLRLCY4928R546UTKYLJPCMETX2F2NENG5Y258VH-RCCVL89HC23CEWVKHPGUFT5NG2PA2CE8AX2WX9AVNPFXSVT79SR7RGGXJ9D648JK'}
kr={
    'username':'namnguyen',
    'id':8969,
    'date':'06/06/2023',
    'value':80,
    'name':'base vn api post request',
    'confidence':'high',
    'workload':5,
    'content':'adsda'
}
kpi={
    'username':'thinhle',
    'id':10967,
    'date':'17/07/2023',
    'value':60,
    'name':'Check in to goal/kpi Gross Margin: 40 (%)',
    'content':''
}

# query_string="SELECT * FROM `pacc-analytics.nam_pacc.metrics_reverse_to_base`"
#
#a = big_query.bq_pandas(query_string)
#a['value'] = a['value'].astype(int)
#b=a.to_dict('records')
#
#for b_dict in b:
#    print(b_dict)
#    d={**access_token,**b_dict}
#    
#    response=requests.post(url,data=d)
#    print(response)
