import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import big_query


schema_to_append='GOOGLE_SHEETS'
schema_appended='PAST_TARGET'
table_id='daily_sale_targets'

big_query.append_tables(schema_to_append,schema_appended,table_id)