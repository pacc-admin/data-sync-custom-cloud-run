import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow,big_query,dict_function

brand='BGN'
schema='IPOS_CRM_'+brand
table='member_vouchers'
list_pos_order = [
    'Id',
    'Phone_Number',
    'Pos_Name',
    'Pos_Parent',
    'Pos_Address',
    'Image_Path',
    'Image_Path_Thumb'
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
        "dm_pos_parent": {
            "id": d.get("id",""),
            "description": d.get("description",""),
            "image": d.get("image",""),
            "ahamove_id": d.get("ahamove_id",""),
            "name": d.get("name",""),
            "is_gift_point": d.get("is_gift_point",""),
            "is_send_sms": d.get("is_send_sms",""),
            "pos_type": d.get("pos_type",""),
            "Brand_Name": d.get("Brand_Name",""),
            "Sms_Partner": d.get("Sms_Partner",""),
            "Direct_List": d.get("Direct_List",""),
            "Msg_Member_Bad_Rate": d.get("Msg_Member_Bad_Rate",""),
            "Logo_Image": d.get("Logo_Image",""),
            "Pos_Feature": d.get("Pos_Feature",""),
            "Manager_Phone": d.get("Manager_Phone",""),
            "Manager_Email_List": d.get("Manager_Email_List",""),
            "Hotline": d.get("Hotline",""),
            "Member_Parnter_Id": d.get("Member_Parnter_Id",""),
            "Limit_Eat_Count_Per_Day": d.get("Limit_Eat_Count_Per_Day",""),
            "Limit_Pay_Amount_Per_Day": d.get("Limit_Pay_Amount_Per_Day",""),
            "Company_Id": d.get("Company_Id",""),
            "Checkin_Time": d.get("Checkin_Time",""),
            "Estimate_Complete_Order_Time": d.get("Estimate_Complete_Order_Time",""),
            "Using_Cloud_Loyalty": d.get("Using_Cloud_Loyalty",""), 
            "Using_Ipos_Otp": d.get("Using_Ipos_Otp",""), 
            "Booking_Type": d.get("Booking_Type",""),
            "Msg_Up_Membership": d.get("Msg_Up_Membership",""),
            "App_Id": d.get("App_Id",""),
            "Ws_Sip_Server": d.get("Ws_Sip_Server",""),
            "Pass_Sip_Server": d.get("Pass_Sip_Server",""),
            "Manager_App_Id": d.get("Manager_App_Id" "")       
        
        },
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


