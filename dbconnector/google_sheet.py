from threading import Thread
import gspread
import pandas as pd
import pd_process
import os

class gg_sheet_import():
    def __init__(self,file_name):
        self.file_name=file_name
        print('init method called')

    def __enter__(self):
        print('enter method called')
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('exit method called')

    def gg_sheet_connect(self):
        service_account_file_path=os.environ.get("PACC_SA_RAW")
        gc = gspread.service_account(filename=service_account_file_path)
        sh = gc.open(self.file_name)
        return sh
    
    def list_all_sheets(self):
        sh=self.gg_sheet_connect()
        worksheet_list = sh.worksheets()
        number_of_sheets = len(worksheet_list)
        return number_of_sheets

    def sheet_to_pd(self):
        sh=self.gg_sheet_connect()
        df=pd.DataFrame()
        number_of_sheets=self.list_all_sheets()

        for i in range(0,number_of_sheets):
            worksheet = sh.get_worksheet(i)
        
            list_of_lists = worksheet.get_all_values()
            df_i=pd.DataFrame(list_of_lists)
            
            #set column names equal to values in row index position 0
            df_i.columns = df_i.iloc[0]
            
            #remove first row from DataFrame
            df_i = df_i[1:]

            df=pd.concat([df,df_i])
        
        pd_process.pd_type_change(df)

        #add loaded date field
        df['loaded_date'] = pd.to_datetime('today')
        print(df)
    
        return df

    def clear_sheet(self):
        sh=self.gg_sheet_connect()
        for i in range(0,self.number_of_sheets):
            worksheet = sh.get_worksheet(i)
            worksheet.clear()
            print('success')