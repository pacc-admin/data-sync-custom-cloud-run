import pandas as pd
import time
from datetime import datetime, timedelta

def get_yesterday():
    today = datetime.today()
    two_day_before = today - timedelta(days=2)
    two_day_before_unix = time.mktime(two_day_before.timetuple())
    return two_day_before

def pd_update_latest(dataset,last_update):
    final_dataset = dataset[dataset[last_update].astype('float') > get_yesterday()]
    return final_dataset
                       