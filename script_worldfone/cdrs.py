import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import worldfone

schema='WORLDFONE'
table_id='cdrs'

worldfone.worldfone_bq(schema,table_id)