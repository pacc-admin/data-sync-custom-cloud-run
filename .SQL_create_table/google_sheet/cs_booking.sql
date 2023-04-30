create or replace table `pacc-raw-data.BOOKING_DATA.cs_booking` (
    outlet_code string,
    created_by string,
    booking_date string,
    reservation_date string,
    booking_hours string,
    customer_name string,
    phone string,
    pax1 string,
    note string,
    customer_order string,
    deposit string,
    channel string,
    zone string,
    customer_status string,
    pax2 string,
    round string,
    weekday string,
    month string,
    year string,
    shift string,
    cs_call string,
    thoi_gian_goi_ string,
    level_of_customer_satisfaction string,
    customer_feedback string,
    loaded_date timestamp
)

partition by date(loaded_date)