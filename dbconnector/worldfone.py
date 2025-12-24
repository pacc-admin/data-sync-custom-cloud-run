import requests
import time
import pandas as pd
from datetime import datetime
from .big_query import bq_insert, bq_delete, bq_pandas
from yml_extract import etract_variable_yml_string
from time_function import last_unix_t_of_month,convert_unix_to_date,unix_month_no,last_date_of_month


def get_worldfone_api(startdate,enddate,page=1):
    worldfone_key=etract_variable_yml_string(dictionary_1='worldfone',dictionary_2='secret_key',file_name='worldfone_key')
    url='https://apps.worldfone.vn/externalcrm/getcdrs.php?secret='+str(worldfone_key)+'&startdate='+str(startdate)+'&enddate='+str(enddate)+'&page='+str(page)+'&pageSize=100'
    print(url)
    raw_output = requests.post(url).json()
    
    return raw_output

def worldfone_pd(start_date,end_date):

    #getting total pages
    data_to_insert=pd.DataFrame()
    raw_output = get_worldfone_api(startdate=start_date,enddate=end_date)
    print("=== DEBUG raw_output ===")
    print(raw_output)
    
    # Handle API error responses
    if isinstance(raw_output, dict):
        if 'code' in raw_output and raw_output.get('code') == 0:
            print(f"API Error: {raw_output.get('messages', {}).get('text', 'Unknown error')}")
            return data_to_insert
        if raw_output.get('total', 0) == 0 and raw_output.get('data', []) == []:
            print("No data available for this period")
            return data_to_insert
        total_pages = raw_output.get('max_page', 0) + 1
    else:
        print(f"Unexpected API response: {raw_output}")
        return data_to_insert
        
    print('Total page is '+str(total_pages))

    #concat df to all pages data
    for page in range(1,total_pages):
        raw_output = get_worldfone_api(startdate=start_date,enddate=end_date,page=page)
        if 'data' not in raw_output:
            print(f"No data in response for page {page}")
            continue
        df = pd.DataFrame(raw_output['data'])
        data_to_insert = pd.concat([data_to_insert,df])
        data_to_insert['loaded_date'] = pd.to_datetime('today')
    
    return data_to_insert

def worldfone_bq(schema,table_id):
    query_string = "select max(unix_seconds(timestamp(calldate || ' UTC+7'))) as calldate FROM "+'`pacc-raw-data.'+schema+'.'+table_id+'`'
    start_date = bq_pandas(query_string)['calldate'].astype(int).to_list()[0] + 1
    end_date = int(time.mktime(datetime.today().timetuple()))

    print('start date is'+str(start_date))
    print('end date is'+str(end_date))

    if unix_month_no(end_date) == unix_month_no(start_date):
        end_date = end_date
    else:
        end_date = last_unix_t_of_month(start_date)

    data_to_insert = worldfone_pd(start_date,end_date=end_date)

    if data_to_insert.to_dict('records')==[]:
        
        if last_date_of_month(start_date)==convert_unix_to_date(start_date) and end_date==last_unix_t_of_month(start_date):
                
                #if last date and end date fall into last date of month => switch range to next date of month
                start_date=end_date+1
                end_date=last_unix_t_of_month(start_date)
                data_to_insert=worldfone_pd(start_date,end_date=end_date)

                if data_to_insert.to_dict('records')==[]:
                    result='No Insert'
                    print('end')
                
                else:
                    print('continue')
                    #remove column with id matches the inserted rows from worldphone
                    unique_key=data_to_insert['uniqueid']+data_to_insert['direction']
                    row_to_exclude="('"+"','".join(unique_key.to_list())+"')"
                    condition='concat(uniqueid,direction) in'+row_to_exclude
            
                    result=bq_insert(
                                schema,
                                table_id,
                                dataframe=data_to_insert,
                                condition=condition
                            )
                    print('end')

        else:
            result='No Insert'
            print('end')
        
    else:
        print('continue')
        #remove column with id matches the inserted rows from basevn
        unique_key=data_to_insert['uniqueid']+data_to_insert['direction']
        row_to_exclude="('"+"','".join(unique_key.to_list())+"')"
        condition='concat(uniqueid,direction) in'+row_to_exclude

        result=bq_insert(
                    schema,
                    table_id,
                    dataframe=data_to_insert,
                    condition=condition
                )
        print('end')

    print(start_date)
    print(end_date)
    print(result)
    return result

def worldfone_bq_historical(schema,table_id):
    # Get last processed date from BigQuery
    query_string = "select max(unix_seconds(timestamp(calldate || ' UTC+7'))) as calldate FROM "+'`pacc-raw-data.'+schema+'.'+table_id+'`'
    start_date = bq_pandas(query_string)['calldate'].astype(int).to_list()[0] + 1
    
    # Convert current time to UTC+7 for consistency
    utc_offset = 7 * 3600  # 7 hours in seconds
    today_unix = int(time.time()) + utc_offset
    
    order = 0
    while start_date <= today_unix:
        order = order + 1
        print(f"\nProcessing batch {order}")
        
        # Convert timestamps to datetime for better month handling
        start_dt = datetime.fromtimestamp(start_date)
        
        # Calculate end of current month in UTC+7
        if start_dt.month == 12:
            next_month = start_dt.replace(year=start_dt.year + 1, month=1)
        else:
            next_month = start_dt.replace(month=start_dt.month + 1)
        end_date = int(next_month.timestamp()) - 1
        
        # Don't process future data
        end_date = min(end_date, today_unix)
        
        print(f"Start date: {datetime.fromtimestamp(start_date).strftime('%Y-%m-%d %H:%M:%S')} UTC+7")
        print(f"End date: {datetime.fromtimestamp(end_date).strftime('%Y-%m-%d %H:%M:%S')} UTC+7")
        
        # Get data for this month
        data_to_insert = worldfone_pd(start_date, end_date)
        
        if data_to_insert.to_dict('records'):
            print('continue')
            # Remove existing records that match the new data
            unique_key = data_to_insert['uniqueid'] + data_to_insert['direction']
            row_to_exclude = "('" + "','".join(unique_key.to_list()) + "')"
            condition = 'concat(uniqueid,direction) in' + row_to_exclude
            
            bq_insert(
                schema,
                table_id,
                dataframe=data_to_insert,
                condition=condition
            )
            print(f"Successfully inserted data for period")
        else:
            print('No data for this period')
        
        # Move to start of next month
        start_date = end_date + 1
        
        # Stop if we've reached today
        if end_date >= today_unix:
            break
            
        print(' ')




import calendar  # Thêm thư viện này ở đầu file nếu chưa có

def worldfone_bq_historical_v2(schema, table_id):
    # 1. Lấy thời gian dữ liệu cuối cùng trong BQ
    query_string = "select max(unix_seconds(timestamp(calldate || ' UTC+7'))) as calldate FROM "+'`pacc-raw-data.'+schema+'.'+table_id+'`'
    
    try:
        bq_result = bq_pandas(query_string)['calldate'].astype(float).to_list()[0]
        # Nếu DB có dữ liệu, bắt đầu từ giây tiếp theo
        # Nếu DB trả về NaN (chưa có dữ liệu), bạn cần set một ngày mặc định (ví dụ: epoch 0 hoặc một ngày cụ thể)
        if pd.isna(bq_result):
            # Ví dụ: Mặc định lấy từ đầu năm 2024 nếu bảng rỗng (tuỳ bạn chỉnh)
            start_date = int(datetime(2024, 1, 1).timestamp())
        else:
            start_date = int(bq_result) + 1
    except Exception as e:
        print(f"Error getting max date: {e}")
        return

    # 2. Xác định thời điểm hiện tại (Today)
    # Lưu ý: Unix timestamp là độc lập múi giờ, nhưng việc tính toán 'hôm nay' cần nhất quán.
    # Code cũ của bạn cộng thêm offset, ta giữ nguyên logic đó để khớp với hệ thống của bạn.
    utc_offset = 7 * 3600 
    today_unix = int(time.time()) + utc_offset

    order = 0
    
    # 3. Vòng lặp xử lý từng khoảng thời gian
    while start_date <= today_unix:
        order += 1
        print(f"\n=== Processing batch {order} ===")
        
        # Convert start_date sang datetime để tính toán lịch
        start_dt = datetime.fromtimestamp(start_date)
        
        # --- LOGIC QUAN TRỌNG NHẤT ---
        # Tính toán ngày cuối cùng của tháng hiện tại (End of Month)
        # calendar.monthrange(year, month) trả về (thứ đầu tuần, số ngày trong tháng)
        days_in_month = calendar.monthrange(start_dt.year, start_dt.month)[1]
        
        # Tạo thời điểm giây cuối cùng của tháng hiện tại
        # Ví dụ: start là 15/11, thì end_of_month là 30/11 23:59:59
        end_of_month_dt = start_dt.replace(day=days_in_month, hour=23, minute=59, second=59)
        end_of_month_ts = int(end_of_month_dt.timestamp())
        
        # End date thực tế của batch này sẽ là Min(Cuối tháng, Hiện tại)
        # Điều này đảm bảo:
        # 1. Không bao giờ vượt quá tháng hiện tại (tránh lỗi 108)
        # 2. Không bao giờ lấy dữ liệu tương lai (vượt quá today)
        end_date = min(end_of_month_ts, today_unix)
        
        # In ra log để kiểm tra
        print(f"Range: {datetime.fromtimestamp(start_date).strftime('%Y-%m-%d %H:%M:%S')} -> {datetime.fromtimestamp(end_date).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Gọi hàm lấy dữ liệu
        data_to_insert = worldfone_pd(start_date, end_date)
        
        # Insert vào BigQuery
        if not data_to_insert.empty:
            print(f"Found {len(data_to_insert)} records. Inserting...")
            
            # Logic cũ: Xóa duplicate trước khi insert
            unique_key = data_to_insert['uniqueid'] + data_to_insert['direction']
            # Lưu ý: Xử lý chuỗi rỗng hoặc NaN nếu cần thiết trong unique_key
            
            row_to_exclude = "('" + "','".join(unique_key.astype(str).to_list()) + "')"
            condition = 'concat(uniqueid,direction) in' + row_to_exclude
            
            bq_insert(
                schema,
                table_id,
                dataframe=data_to_insert,
                condition=condition
            )
            print("Done insert.")
        else:
            print('No data for this period.')
        
        # --- CHUYỂN SANG BATCH TIẾP THEO ---
        # Batch sau sẽ bắt đầu ngay sau batch này 1 giây
        start_date = end_date + 1
        
        # Nếu start_date mới đã vượt quá thời điểm hiện tại thì dừng
        if start_date > today_unix:
            print("All caught up!")
            break
            
        print('--------------------------------')