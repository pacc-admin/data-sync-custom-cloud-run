from google.cloud import bigquery
from big_query import bq_pandas, bq_query, full_refresh_bq_insert_from_json2
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import datetime
import json_schema_bq
import json
import time
class ipos_crm_el:

    def __init__(
        self,
        brand: str,
        table: str,
        schema: str,

    ):
        self.brand = brand
        self.table = table
        self.schema = schema
        
        # Setup requests Session với retry và connection pooling để tối ưu performance
        self.session = requests.Session()
        
        # Retry strategy: retry 3 lần với exponential backoff
        # Retry cho: connection errors, timeout, SSL errors, và HTTP 5xx errors
        retry_strategy = Retry(
            total=3,  # Tổng số lần retry
            backoff_factor=1,  # Wait 1s, 2s, 4s giữa các lần retry
            status_forcelist=[500, 502, 503, 504],  # Retry cho HTTP errors này
            allowed_methods=["GET"],  # Chỉ retry GET requests
            raise_on_status=False  # Không raise exception, trả về response để xử lý
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Số connection pools
            pool_maxsize=20  # Max connections per pool
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        print('init method called')

    def __enter__(self):
        # If needed, initialize any resources here
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # If needed, clean up any resources here
        pass

    def get_membership_ids(self):
        """Get list of membership_id from sale table"""
        query_string = f'select distinct membership_id from `pacc-prod-data-lake.ab_cdc_ipos_sale_{self.brand.lower()}_2024.SALE`'
        membership_data = bq_pandas(query_string)
        print(f'Total members are {len(membership_data.index)}')
        return membership_data['membership_id'].to_list()

    def crm_api(self, user_id, page=0, max_retries=3):
        """Get data from CRM API for single member with retry logic"""
        url=f'https://api.foodbook.vn/ipos/ws/xpartner/{self.table}'
        params = {
          'access_token': 'ARPP3SFXSJ6R1BW5KNXEJXZV5YNENM60',
          'pos_parent':self.brand,
          'user_id':user_id,
          'page':page
        }
        
        # Retry logic với exponential backoff cho SSL/network errors
        for attempt in range(max_retries):
            try:
                # Dùng session để reuse connection và có retry tự động
                resp = self.session.get(url, params=params, timeout=(10, 30))  # (connect timeout, read timeout)
                break  # Thành công, thoát khỏi retry loop
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f'SSL/Network error for user_id={user_id} (attempt {attempt+1}/{max_retries}), retrying in {wait_time}s: {e}')
                    time.sleep(wait_time)
                else:
                    print(f'Network error when calling CRM for user_id={user_id} after {max_retries} attempts: {e}')
                    return []
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f'Timeout for user_id={user_id} (attempt {attempt+1}/{max_retries}), retrying in {wait_time}s')
                    time.sleep(wait_time)
                else:
                    print(f'Timeout when calling CRM for user_id={user_id} after {max_retries} attempts: {e}')
                    return []
            except requests.RequestException as e:
                # Các lỗi khác không retry
                print(f'Request error when calling CRM for user_id={user_id}: {e}')
                return []

        # check HTTP status
        if not resp.ok:
            # log status and short response for debugging
            txt = resp.text[:1000].strip()
            print(f'CRM API returned status {resp.status_code} for user_id={user_id}; response (truncated): {txt}')
            return []

        # try parse JSON safely
        try:
            data_json = resp.json()
        except ValueError as e:
            # JSON decode error
            txt = resp.text[:2000].strip()
            print(f'Invalid JSON from CRM for user_id={user_id}: {e}; response (truncated): {txt}')
            return []

        # extract 'data' key
        try:
            return data_json.get('data', [])
        except Exception:
            print(f'Unexpected JSON structure from CRM for user_id={user_id}: {data_json}')
            return []

    def crm_get_full_list(self):
        """Get data from CRM API for all member"""
        user_ids = self.get_membership_ids()
        total_members = len(user_ids)
        print(f'Processing {total_members} members...')
        #user_id_list=['84903003380','84907090991','84968757511','84982050271','84909151071','84973382047','84901632068','84907090991']
        #user_id_list=['841253021716','84909998674']
    
        raw_output=[]
        processed = 0
        failed = 0
        start_time = time.time()
        
        for idx, user_id in enumerate(user_ids, 1):
            # Log progress mỗi 100 members hoặc ở 10% intervals
            if idx % 100 == 0 or idx % max(1, total_members // 10) == 0:
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                remaining = (total_members - idx) / rate if rate > 0 else 0
                print(f'Progress: {idx}/{total_members} ({idx*100//total_members}%) | '
                      f'Processed: {processed} | Failed: {failed} | '
                      f'Rate: {rate:.1f} members/s | ETA: {remaining:.0f}s')
            
            raw_output_member = self.crm_api(user_id)
    
            if not raw_output_member:
                failed += 1
                continue
            
            processed += 1

            updated_data = []
            if isinstance(raw_output_member, dict):  # If it's a dictionary, convert it to a list
                raw_output_member = [raw_output_member]
            for row in raw_output_member:
                if isinstance(row, str):
                    print(f"Skipping invalid row for user_id: {user_id}")
                    continue
                updated_dict = row.copy()
                updated_dict['membership_id'] = user_id
                updated_dict['loaded_date'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f UTC')
                updated_data.append(updated_dict)   
                                         
            raw_output.extend(updated_data)

        elapsed = time.time() - start_time
        print(f'Completed: {processed}/{total_members} members processed successfully, '
              f'{failed} failed, {len(raw_output)} total records, '
              f'took {elapsed:.1f}s ({elapsed/60:.1f} minutes)')
        return raw_output
    
    def bq_load(self):
        """Get data from CRM API for all members"""
        file_path = f'metadata/ipos_crm/{self.table}.json'

        # obtain json schema
        job_config = bigquery.LoadJobConfig(
            schema=json_schema_bq.parse_json_schema_from_file(file_path),
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema_update_options=['ALLOW_FIELD_ADDITION']
        )

        source_output = self.crm_get_full_list()
        
        # DEBUG only
        # a= json.dumps(source_output, indent =4)
        # with open('sample1.json','w') as f:
        #     f.write(a)       
        # with open('sample1.json') as f:
        #     source_output = json.load(f) 

        try:
            full_refresh_bq_insert_from_json2(
                source_output, 
                schema = self.schema,
                table_id=self.table,
                job_config=job_config
            )
        except Exception as e:
            print(f'An error occurred while inserting data: {e}')
            print(f'recreate table {self.table}')
            bq_query(f'create or replace table `pacc-raw-data.{self.schema}.{self.table}` (loaded_date timestamp)')
            full_refresh_bq_insert_from_json2(
                source_output, 
                schema = self.schema,
                table_id=self.table,
                job_config=job_config
            )


