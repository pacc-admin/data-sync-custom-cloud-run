import dbconnector
import requests
import pandas as pd
import inflect
class base_bq:
    def data_process(self,column_name,raw_output):
        p = inflect.engine()
        column_name_plural=p.plural(column_name)
        print('step 2')
        dataset = pd.DataFrame(raw_output)
        flatten = pd.json_normalize(dataset[column_name_plural])
        try:
            dataset_final=dbconnector.pd_update_latest(dataset=flatten,last_update='last_update')
        except:
            dataset_final=flatten
        return dataset_final

    def payroll_bq_insert(self,schema,table_id,dataframe):
        client=dbconnector.connect_to_bq()
        print('step 3')
        dbconnector.bq_insert(client,schema,table_id,dataframe)
    
    def while_loop_page_insert(self,page,column_name,table_id):
        pageno=-1
        r=dbconnector.base_vn_connect(app='payroll',component1=column_name)
        total_page=dbconnector.total_page(r)

        while pageno < total_page:
            pageno=pageno+1
            r=dbconnector.base_vn_connect(app='payroll',component1=column_name,page=pageno)
            dataframe= self.data_process(column_name,raw_output=r)
            
            if dataframe.to_dict('records')==[]:
                print('end')
            else:
                print('continue')
                self.payroll_bq_insert(schema,table_id,dataframe)
                print('end')

lists = { 'list1':'cycle',
          'list2':'payroll',
          'list3':'record',
}

if __name__ == '__main__':
    for c2,c1 in lists.items():
        #date_update_unix=dbconnector.get_two_day_before()
        page=0
        schema='BASEVN_PAYROLL'
        print(c1)

        s=base_bq()        
        s.while_loop_page_insert(page=page,column_name=c1,table_id=c1)
