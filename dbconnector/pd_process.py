import pandas as pd
import time
from datetime import datetime, timedelta
from big_query import bq_pandas
import math
import numpy as np

def get_two_day_before():
    today = datetime.today()
    two_day_before = today - timedelta(days=20)
    two_day_before_unix = int(time.mktime(two_day_before.timetuple()))
    return two_day_before_unix


def pd_update_latest(dataset,last_update):
    df = dataset[dataset[last_update].astype('float') > get_two_day_before()]
    return df
        
                      
def pd_nested_schema(df,column,mode='normalized'):
    if mode=='normalized':
      processed_df=pd.json_normalize(df[column])
    else:
      processed_df=df.explode(column)[column].apply(pd.Series)
    processed_df.columns = column+'_' + processed_df.columns
    return processed_df


def pd_last_update(df,query_string_incre,column_updated='last_update'):
    try:
        bq_table_date=bq_pandas(query_string_incre)[column_updated].astype(float).to_list()[0]
        if math.isnan(bq_table_date)==True:
            last_updated_date=0
        else:
            last_updated_date=bq_table_date
    except:
        last_updated_date=0

    try:
        latest_dataset = df[df[column_updated].astype('float') > last_updated_date]
    except:
        latest_dataset=df
    return latest_dataset


def pd_type_change(df,columns=[],converted_type=str,type='exclude'):
    column_list = list(df.columns)
    if columns==[]:
        df[column_list]=df[column_list].astype(converted_type)
    else:
        for word in columns:
            try:
                column_list.remove(word)
            except:
                column_list

    if type=='exclude':
        column_to_convert=column_list
    else:
        column_to_convert=columns

    if converted_type==int:
        df[column_to_convert]=df[column_to_convert].astype(np.float).astype("Int32")
    else:
        df[column_to_convert]=df[column_to_convert].astype(converted_type)

    df.apply(pd.Series)

    return df

