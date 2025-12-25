import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import sys
from datetime import datetime, timedelta
import pytz
import pandas as pd
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from big_query import bq_insert, bq_latest_date, bq_delete, connect_to_bq

# ENV
PROJECT_ID = 'pacc-raw-data'
DATASET = 'INVOICE_DATASET'
TABLE = 'minvoice_invoices'
TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')
API_URL = "https://0314142245.minvoice.app/api/InvoiceApi78/GetInvoices"
API_TOKEN = "O87316arj5+Od3Fqyy5hzdBfIuPk73eKqpAzBSvv8sY="
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}",
    "User-Agent": "PostmanRuntime/7.36.0"
}

# -- Helper Functions --
def get_arg(idx, default=None):
    try:
        return sys.argv[idx]
    except IndexError:
        return default

def get_dates():
    today = datetime.now(TIMEZONE).date()
    default_start = datetime(2024, 9, 5).date()
    start_arg = get_arg(1)
    end_arg = get_arg(2)
    
    # Check if arguments are valid date strings, skip if they look like command flags
    def is_valid_date(arg):
        if not arg or arg.startswith('--'):
            return False
        try:
            datetime.strptime(arg, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    start_date = (
        datetime.strptime(start_arg, '%Y-%m-%d').date() if is_valid_date(start_arg) else default_start
    )
    end_date = (
        datetime.strptime(end_arg, '%Y-%m-%d').date() if is_valid_date(end_arg) else today
    )
    return start_date, end_date

def table_exists():
    """
    True nếu bảng đã tồn tại (dù có hay không có dữ liệu)
    """
    client = connect_to_bq()
    table_id_full = f'{PROJECT_ID}.{DATASET}.{TABLE}'
    try:
        client.get_table(table_id_full)
        return True
    except Exception as e:
        # NotFound: bảng không tồn tại
        return False

def create_table_if_needed():
    client = connect_to_bq()
    table_id_full = f'{PROJECT_ID}.{DATASET}.{TABLE}'
    # Gọi API 1 ngày để lấy schema mẫu
    khieu_sample = f"1C{2024 % 100:02d}MPA"
    payload = {
        "tuNgay": "2024-09-05",
        "denngay": "2024-09-05",
        "khieu": khieu_sample,
        "start": 0,
        "count": 1,
        "coChiTiet": True
    }
    response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
    result = response.json()
    list_data = result.get("data", [])
    if not list_data:
        raise Exception("Không xác định được schema bảng vì API trả về trống")
    df = pd.DataFrame(list_data)
    # BigQuery schema
    fields = []
    partition_field = None
    for col, dtype in df.dtypes.items():
        if col == "inv_invoiceIssuedDate":
            partition_field = col
            fields.append(f"  `{col}` TIMESTAMP")
        elif pd.api.types.is_integer_dtype(dtype):
            fields.append(f"  `{col}` INT64")
        elif pd.api.types.is_float_dtype(dtype):
            fields.append(f"  `{col}` FLOAT64")
        elif pd.api.types.is_bool_dtype(dtype):
            fields.append(f"  `{col}` BOOL")
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            fields.append(f"  `{col}` TIMESTAMP")
        else:
            fields.append(f"  `{col}` STRING")
    
    fields.append(f"  `loaded_at` TIMESTAMP") 


    schema_sql = ",\n".join(fields)
    part_sql = f"\nPARTITION BY DATE(`{partition_field}`)\n" if partition_field else ""
    create_sql = f"CREATE TABLE `{table_id_full}` (\n{schema_sql}\n){part_sql}"
    try:
        client.query(create_sql).result()
        print(f"Table created: {table_id_full} (partition on {partition_field if partition_field else 'none'})")
    except Exception as e:
        print(f"Table create failed (possibly exists): {e}")

def process_date(cur_date, batch_size=300):
    all_df = []
    offset = 0
    now_timestamp = datetime.now(TIMEZONE)
    khieu = f"1C{cur_date.year % 100:02d}MPA"
    while True:
        payload = {
            "tuNgay": cur_date.strftime('%Y-%m-%d'),
            "denngay": cur_date.strftime('%Y-%m-%d'),
            "khieu": khieu,
            "start": offset,
            "count": batch_size,
            "coChiTiet": True
        }
        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
            result = response.json()
            if response.status_code == 200 and result.get("ok"):
                list_data = result.get("data", [])
                if list_data:
                    df = pd.DataFrame(list_data)
                    if not df.empty:
                        df['loaded_at'] = now_timestamp
                        print(f"Fetched {len(df)} records for {cur_date}, offset {offset}")
                        bq_insert(DATASET, TABLE, df)
                        all_df.append(df)
                        offset += batch_size
                        # If less than batch_size, no more pages
                        if len(df) < batch_size:
                            break
                    else:
                        print(f"Empty dataframe for {cur_date}, offset {offset}")
                        break
                else:
                    print(f"No data for {cur_date}, offset {offset}")
                    break
            else:
                print(f"API Error {cur_date} offset {offset}: {result.get('message')}")
                break
        except Exception as e:
            print(f"Exception {cur_date} offset {offset}: {e}")
            break
    num_rows = sum(len(x) for x in all_df)
    return num_rows

def ingest_api_range(start_date, end_date, batch_size=300, max_workers=10):
    date_list = []
    cur_date = start_date
    while cur_date <= end_date:
        date_list.append(cur_date)
        cur_date += timedelta(days=1)
    
    total_ingested = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_date, date, batch_size): date for date in date_list}
        for future in as_completed(futures):
            num_rows = future.result()
            total_ingested += num_rows
            date = futures[future]
            if num_rows == 0:
                print(f"No data ingested for {date}")
            else:
                print(f"Total ingested for {date}: {num_rows} rows")
    print(f"Grand total rows ingested: {total_ingested}")

def main():
    start_date, end_date = get_dates()
    print(f"Ingest from {start_date} to {end_date}")
    yesterday = datetime.now(TIMEZONE).date() - timedelta(days=1)
    today = datetime.now(TIMEZONE).date()

    if not table_exists():
        print(f"Table chưa tồn tại, tạo mới...")
        create_table_if_needed()

    if table_exists():

        five_days_ago = today - timedelta(days=5)
        condition = f"DATE(inv_invoiceIssuedDate) >= '{five_days_ago}' AND DATE(inv_invoiceIssuedDate) <= '{yesterday}'"
        bq_delete(DATASET, TABLE, condition)
        print(f"Deleted data from {five_days_ago} to {yesterday}")

        last = bq_latest_date('inv_invoiceIssuedDate', DATASET, TABLE)
        if last and last != '1970-01-01':
            last_date = datetime.strptime(last, '%Y-%m-%d').date()
            next_date = last_date + timedelta(days=1)
        else:
            next_date = datetime(2024, 9, 5).date()
        # Nếu đã cập nhật đến >= hôm qua thì không cần ingest nữa
        if next_date > yesterday:
            print(f"Data is up to date. BQ đến {last}, hôm qua là {yesterday}. Không cần ingest!")
            return
        ingest_api_range(next_date, yesterday)
    else:
        # Không có bảng (vừa tạo) => full ingest đến hôm qua
        yesterday = datetime.now(TIMEZONE).date() - timedelta(days=1)
        ingest_api_range(datetime(2024, 9, 5).date(), yesterday)

if __name__ == "__main__":
    main()
