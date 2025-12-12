import gspread
import re
import pandas as pd
import pd_process
import os
import unidecode

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
        # Prefer explicit PACC_SA_RAW, fall back to GOOGLE_APPLICATION_CREDENTIALS
        service_account_file_path = os.environ.get("PACC_SA_RAW") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not service_account_file_path:
            raise RuntimeError("No service account path set: please set PACC_SA_RAW or GOOGLE_APPLICATION_CREDENTIALS environment variable")

        gc = gspread.service_account(filename=service_account_file_path)
        sh = gc.open(self.file_name)
        return sh
    
    def list_all_sheets(self):
        sh=self.gg_sheet_connect()
        worksheet_list = sh.worksheets()
        number_of_sheets = len(worksheet_list)
        return number_of_sheets

    def sheet_to_pd_index(self):
        sh=self.gg_sheet_connect()
        df=pd.DataFrame()
        number_of_sheets=self.list_all_sheets()

        for i in range(0,number_of_sheets):
            print(i)
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

    def sheet_to_pd_name(self,sheet_names,column_to_clean=''):
        sh=self.gg_sheet_connect()
        df=pd.DataFrame()
        for sheet_name in sheet_names:
            print(sheet_name)
            worksheet = sh.worksheet(sheet_name)
            
            list_of_lists = worksheet.get_all_values()
            df_sheet_names=pd.DataFrame(list_of_lists)

            #set column names equal to values in row index position 0
            df_sheet_names.columns = df_sheet_names.iloc[0]
            cleaned_cols=[]
            for col in df_sheet_names.columns:
                space_cleaned=col.lower().replace(' ', '_')
                remove_vn_key=unidecode.unidecode(space_cleaned)
                cleaned_col=re.findall('[a-z0-9_]+',remove_vn_key)
                cleaned_cols=cleaned_cols+[cleaned_col[0]]

            df_sheet_names.columns=cleaned_cols

            #remove first row from DataFrame
            df_sheet_names = df_sheet_names[1:]

            #drop null
            if column_to_clean=='':
                print('no drop')
            else:
                print('drop null')
                df_sheet_names=df_sheet_names[df_sheet_names[column_to_clean]!=''] 
                print(df_sheet_names)
            
            #concat all df sheets
            df=pd.concat([df,df_sheet_names])
        
        #add loaded date field
        df['loaded_date'] = pd.to_datetime('today')
        
    
        return df

    def clear_sheet(self):
        sh=self.gg_sheet_connect()
        for i in range(0,self.number_of_sheets):
            worksheet = sh.get_worksheet(i)
            worksheet.clear()
            print('success')