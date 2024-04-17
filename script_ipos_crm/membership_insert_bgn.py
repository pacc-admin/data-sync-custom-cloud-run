import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query

brand='BGN'
schema='IPOS_CRM_'+brand
table='membership_detail'
column_updated='update_at'
order = [
    "id",
    "user_id",
    "alias_name",
    "full_address",
    "extend_address",
    "district",
    "city",
    "country",
    "city_id",
    "district_id",
    "longitude",
    "latitude",
    "created_at"
]

#execute
source_output=ipos_crm_flow.crm_get_full_list(brand,table)
print(source_output)
source_output_sorted = [
    {
        "id": d.get("id",""),
        "phone_number": d.get("phone_number",""),
        "pos_parent": d.get("pos_parent",""),
        "name": d.get("name", ""),
        "address": [dict(sorted(item.items(), key=lambda x: order.index(x[0]))) for item in d["address"]],
        "membership_type_id": d.get("membership_type_id",""),
        "membership_type_name": d.get("membership_type_name",""),
        "gender": d.get("gender",""),
        "city_id": d.get("city_id",""),
        "city_name": d.get("city_name",""),
        "zalo_id": d.get("zalo_id",""),
        "zalo_join_at": d.get("zalo_join_at",""),
        "point": d.get("point",""),
        "payment_amount": d.get("payment_amount",""),
        "point_amount": d.get("point_amount",""),
        "eat_times": d.get("eat_times",""),
        "first_eat_date": d.get("first_eat_date",""),
        "last_eat_date": d.get("last_eat_date",""),
        "update_at": d.get("update_at",""),
        "last_pos": d.get("last_pos",""),
        "last_pos_name": d.get("last_pos_name",""),
        "created_by": d.get("created_by",""),
        "created_at": d.get("created_at",""),
        "membership_id_new": d.get("membership_id_new",""),
        "tags": d.get("tags",[]),
        "membership_type_change_at": d.get("membership_type_change_at",""),
        "membership_id": d.get("membership_id",""),
        "loaded_date": d.get("loaded_date","")        

    }
    for d in source_output
]

import json
# Serializing json
json_object = json.dumps(source_output, indent=4)
 
# Writing to sample.json
with open("sample1.json", "w") as outfile:
    outfile.write(json_object)

source_output_sorted

try:
   big_query.full_refresh_bq_insert_from_json(source_output_sorted,schema,table_id=table)
except:
   query_string = 'create or replace table '+schema+'.'+table+' (loaded_date timestamp)'
   big_query.bq_query(query_string)
   big_query.full_refresh_bq_insert_from_json(source_output_sorted,schema,table_id=table)
