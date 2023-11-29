import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query,dict_function

brand='5WINE'
schema='IPOS_CRM_'+brand
table='member_vouchers'
dm_pos_parent_order = [
    "id",				
    "name",
    "description",				
    "Using_Ipos_Otp",				
    "Estimate_Complete_Order_Time",				
    "Checkin_Time",				
    "Limit_Eat_Count_Per_Day",				
    "Brand_Name",				
    "Pass_Sip_Server",				
    "Manager_App_Id",				
    "Limit_Pay_Amount_Per_Day",				
    "Sms_Partner",				
    "is_send_sms",				
    "Pos_Feature",				
    "Msg_Up_Membership",				
    "Logo_Image",				
    "Member_Parnter_Id",				
    "is_gift_point",				
    "Msg_Member_Bad_Rate",				
    "Direct_List",				
    "Ws_Sip_Server",				
    "pos_type",				
    "Booking_Type",				
    "Using_Cloud_Loyalty",				
    "App_Id",				
    "Manager_Phone",				
    "ahamove_id",				
    "Company_Id",				
    "Manager_Email_List",				
    "image"		
]

list_pos_order = [
    "Image_Path_Thumb",				
    "Image_Path",				
    "Pos_Address",				
    "Pos_Name",				
    "Phone_Number",				
    "Pos_Parent",				
    "Id"
]

#execute
source_output=ipos_crm_flow.crm_get_full_list(brand,table)
source_output_sorted = [
    {
        "used_sale_tran_id": d.get("used_sale_tran_id",""),
        "used_date": d.get("used_date",""),
        "preferential_type": d.get("preferential_type",""),
        "membership_id": d.get("membership_id",""),
        "limit_discount_item": d.get("limit_discount_item",""),
        "same_price": d.get("same_price",""),
        "discount_per_item": d.get("discount_per_item",""),
        "number_item_free": d.get("number_item_free",""),
        "number_item_buy": d.get("number_item_buy",""),
        "pos_parent": d.get("pos_parent",""),
        "apply_item_type": d.get("apply_item_type",""),
        "loaded_date": d.get("loaded_date",""),
        "only_coupon": d.get("only_coupon",""),
        "used_member_info": d.get("used_member_info",""),
        "is_coupon": d.get("is_coupon",""),
        "apply_item_id": d.get("apply_item_id",""),
        "discount_one_item": d.get("discount_one_item",""),
        "list_pos_id": d.get("list_pos_id",""),
        "discount_max": d.get("discount_max",""),
        "time_date_week": d.get("time_date_week",""),
        "requied_member": d.get("requied_member",""),
        "is_ots": d.get("is_ots",""),
        "is_delivery": d.get("is_delivery",""),
        "dm_pos_parent": [dict(sorted(d["dm_pos_parent"].items(), key=lambda x: dm_pos_parent_order.index(x[0])))],
        "used_bill_amount": d.get("used_bill_amount",""),
        "used_pos_id": d.get("used_pos_id",""),
        "affiliate_used_total_amount": d.get("affiliate_used_total_amount",""),
        "affiliate_discount_amount": d.get("affiliate_discount_amount",""),
        "affiliate_discount_type": d.get("affiliate_discount_type",""),
        "buyer_info": d.get("buyer_info",""),
        "used_discount_amount": d.get("used_discount_amount",""),
        "status": d.get("status",""),
        "voucher_code": d.get("voucher_code",""),
        "item_type_id_list": d.get("item_type_id_list",""),
        "date_start": d.get("date_start",""),
        "discount_extra": d.get("discount_extra",""),
        "min_quantity_discount": d.get("min_quantity_discount",""),
        "item_id_list": d.get("item_id_list",""),
        "discount_type": d.get("discount_type",""),
        "list_pos": [dict(sorted(item.items(), key=lambda x: list_pos_order.index(x[0]))) for item in d["list_pos"]],
        "time_hour_day": d.get("time_hour_day",""),
        "voucher_campaign_name": d.get("voucher_campaign_name",""),
        "affiliate_id": d.get("affiliate_id",""),
        "date_hash": d.get("date_hash",""),
        "date_created": d.get("date_created",""),
        "discount_amount": d.get("discount_amount",""),
        "date_end": d.get("date_end",""),
        "pos_id": d.get("pos_id",""),
        "amount_order_over": d.get("amount_order_over",""),
        "is_all_item": d.get("is_all_item",""),
        "has_sale_manager": d.get("has_sale_manager",""),
        "voucher_description": d.get("voucher_description",""),
        "voucher_campaign_id": d.get("voucher_campaign_id",""),
        "affiliate_discount_extra": d.get("affiliate_discount_extra",""),

    }
    for d in source_output
]

try:
    big_query.full_refresh_bq_insert_from_json(source_output_sorted,schema,table_id=table)
except:
    query_string = 'create or replace table '+schema+'.'+table+' (loaded_date timestamp)'
    big_query.bq_query(query_string)
    big_query.full_refresh_bq_insert_from_json(source_output_sorted,schema,table_id=table)


