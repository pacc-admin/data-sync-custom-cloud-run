from .big_query import bq_last_update
import datetime

def incremental_dict(raw_output,column_updated,schema,table,column_type='timestamp'):
    if column_type=='timestamp':
        print('skip conversion')
        column_updated_unix=column_updated
    else:
        column_updated_unix=column_updated+'_unix'
        for raw_output_dict in raw_output:
            for key in [column_updated]:
                my_datetime = datetime.datetime.strptime(raw_output_dict[key], '%Y-%m-%d %H:%M:%S')
                raw_output_dict[column_updated_unix] = my_datetime.timestamp()
        

    query_string_incre='select max('+column_updated_unix+') as last_update from `pacc-raw-data.'+schema+'.'+table+'`'
    last_update=bq_last_update(query_string_incre,column_updated=column_updated_unix)

    source_output=[raw_output_dict for raw_output_dict in raw_output if int(raw_output_dict[column_updated_unix]) > last_update]
    return source_output