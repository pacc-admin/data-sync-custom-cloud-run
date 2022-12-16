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
                       