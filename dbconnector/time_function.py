from datetime import datetime
import time
from dateutil.relativedelta import relativedelta

def last_unix_t_of_month(unix_dt):
    dt = datetime.fromtimestamp(unix_dt)
    date_dt=dt.date()
    last_date=date_dt+ relativedelta(day=31)
    last_date_dt=datetime.strptime(str(last_date)+' 23:59:59', "%Y-%m-%d %H:%M:%S")
    
    last_date_unix= int(time.mktime(last_date_dt.timetuple()))
    print('last timestamp of month is: '+str(last_date_unix))
    return last_date_unix