import pandas as pd
import time
from datetime import datetime, timedelta

def get_two_day_before():
    today = datetime.today()
    two_day_before = today - timedelta(days=20)
    two_day_before_unix = int(time.mktime(two_day_before.timetuple()))
    return two_day_before_unix

def pd_update_latest(dataset,last_update):
    final_dataset = dataset[dataset[last_update].astype('float') > get_two_day_before()]
    return final_dataset
                       
def pd_nested_schema(df,column,mode='normalized'):
    if mode=='normalized':
      processed_df=pd.json_normalize(df[column])
    else:
      processed_df=df.explode(column)[column].apply(pd.Series).drop(columns=0,axis=1)
    processed_df.columns = column+'_' + processed_df.columns
    return processed_df