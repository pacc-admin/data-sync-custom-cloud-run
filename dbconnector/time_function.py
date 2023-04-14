from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import dateutil.relativedelta

def last_unix_t_of_month(unix_dt):
    dt = datetime.fromtimestamp(unix_dt)
    date_dt=dt.date()
    last_date=date_dt+ relativedelta(day=31)
    last_date_dt=datetime.strptime(str(last_date)+' 23:59:59', "%Y-%m-%d %H:%M:%S")
    
    last_date_unix= int(time.mktime(last_date_dt.timetuple()))
    print('last timestamp of month is: '+str(last_date_unix))
    return last_date_unix

def first_unix_t_of_last_month(unix_dt):
    dt = datetime.fromtimestamp(unix_dt)
    date_dt=dt.date()
    first_date=date_dt.replace(day=1)
    last_month_date = first_date + dateutil.relativedelta.relativedelta(months=-1)
    last_month_date_dt=datetime.strptime(str(last_month_date)+' 00:00:00', "%Y-%m-%d %H:%M:%S")
    first_date_unix= int(time.mktime(last_month_date_dt.timetuple()))
    print('first timestamp of last month is: '+str(first_date_unix))
    return first_date_unix