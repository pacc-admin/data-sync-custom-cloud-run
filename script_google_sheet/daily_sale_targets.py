import sys, os
from google.cloud import bigquery
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")

from google_sheet import gg_sheet_import
import big_query


schema='GOOGLE_SHEETS'
table_id='daily_sale_targets'

with gg_sheet_import('target_daily') as s:
    dataframe=s.sheet_to_pd_index()
    big_query.bq_insert(schema,table_id,dataframe,condition='true')

