import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

from google_sheet import gg_sheet_import
import big_query

schema='GOOGLE_SHEETS'
table_id='cs_booking'
sheet_names=['data']
column_to_clean='booking_date'

with gg_sheet_import('2025 - Booking system 1.2') as s:
    dataframe=s.sheet_to_pd_name(sheet_names,column_to_clean)
    # If the source sheet renamed a column (e.g. 'pic' -> 'created_by'), normalize here before loading
    if 'pic' in dataframe.columns and 'created_by' not in dataframe.columns:
        dataframe = dataframe.rename(columns={'pic': 'created_by','outletcode':'outlet_code','booking_hour':'booking_hours'
                                              ,'guest_name':'customer_name','pre_ordered':'customer_order'})
    big_query.bq_insert(schema,table_id,dataframe,condition='true')
