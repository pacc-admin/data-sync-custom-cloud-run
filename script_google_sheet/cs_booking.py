import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

from google_sheet import gg_sheet_import
import big_query

schema='GOOGLE_SHEETS'
table_id='cs_booking'
sheet_names=['FW','BGNK','BGQT','BGLQD','BGSH','BGLVS','BGBC','BGXT']
column_to_clean='booking_date'

with gg_sheet_import('Booking system') as s:
    dataframe=s.sheet_to_pd_name(sheet_names,column_to_clean)
    big_query.bq_insert(schema,table_id,dataframe,condition='true')
