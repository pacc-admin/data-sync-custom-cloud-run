from big_query import bq_last_update

def incremental_dict(raw_output,column_updated,schema,table):
    query_string_incre='select max('+column_updated+') as last_update from `pacc-raw-data.'+schema+'.'+table+'`'
    last_update=bq_last_update(query_string_incre,column_updated)
    source_output=[raw_output_dict for raw_output_dict in raw_output if int(raw_output_dict[column_updated]) > last_update]
    return source_output