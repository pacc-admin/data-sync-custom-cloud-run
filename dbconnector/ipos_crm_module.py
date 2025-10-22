from google.cloud import bigquery
from big_query import bq_pandas, bq_query, full_refresh_bq_insert_from_json2
import requests
import datetime
import json_schema_bq
import json
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

    def crm_api(self, user_id, page=0):
        """Get data from CRM API for single member"""
        url=f'https://api.foodbook.vn/ipos/ws/xpartner/{self.table}'
        params = {
          'access_token': 'ARPP3SFXSJ6R1BW5KNXEJXZV5YNENM60',
          'pos_parent':self.brand,
          'user_id':user_id,
          'page':page
        }
        try:
            resp = requests.get(url, params=params, timeout=30)
        except requests.RequestException as e:
            print(f'Network error when calling CRM for user_id={user_id}: {e}')
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
        #user_id_list=['84903003380','84907090991','84968757511','84982050271','84909151071','84973382047','84901632068','84907090991']
        #user_id_list=['841253021716','84909998674']
    
        raw_output=[]
        for user_id in user_ids:
            print(f'get data for member_id: {user_id}')
            raw_output_member = self.crm_api(user_id)
    
            if not raw_output_member:
                print('no data')
                continue

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


