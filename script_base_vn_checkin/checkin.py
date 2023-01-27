import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import base_vn_checkin
    
#varible declaration
schema='BASEVN_CHECKIN'
table_id='checkin_logs'
query_string='select max(logs_time) as logs_time from `pacc-raw-data.'+schema+'.'+table_id+'`'

#execution
with base_vn_checkin.base_vn_checkin_flow() as s:
    s.tranform_logs_to_df(query_string)
    s.df_process()
    s.incremental_update(query_string)
    s.bq_batch_load(schema,table_id)
