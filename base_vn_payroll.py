import dbconnector
import requests
import pandas as pd

class base_bq:
    def base_vn_connect(self,component):
        print('step 1')
        p = {
            "access_token": "7383-HCMUFGYR35XWJDCKFCJ93VNFN89F4PR5H2ALD63V9CCJZXQ948PRBE6BDNJUX29H-YDN58WMY5JWFGPW2EKEXJLJ5PHUH9HKKJDNAX3VCQDGZP4WT55NVR964J6ZAA5WQ"
        }
        
        url="https://payroll.base.vn/extapi/v1/"+component+"/list"
        self.r = requests.get(url, params=p).json()
        
    def data_process(self,column_name):
        print('step 2')
        dataset = pd.DataFrame(self.r)
        flatten = pd.json_normalize(dataset[column_name+"s"])
        return flatten

    def payroll_bq_insert(self,schema,table_id,dataframe):
        client=dbconnector.connect_to_bq()
        print('step 3')
        dbconnector.bq_insert(client,schema,table_id,dataframe)


lists = ['cycle','payroll','record']


if __name__ == '__main__':
    for variable in lists:
        schema='BASEVN_PAYROLL'
        s=base_bq()
        print(variable)
        s.base_vn_connect(variable)
        dataframe= s.data_process(variable)
        if dataframe.to_dict('records')==[]:
            print('end')
        else:
            print('continue')
            s.payroll_bq_insert(schema,variable,dataframe)
