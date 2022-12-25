create or replace table `pacc-raw-data.BASEVN_HRM.office`  (
    id string,
    user_id string,
    name string,
    address string,
    hq string,
    content string,
    metatype string,
    num_people int64,
    phone string,
    email string,
    type string,
    since string,
    last_update string,
    hid string,
    token string,
    data_code string,
    data_phone string,
    data_email string,
    loaded_date timestamp

)

partition by date(loaded_date)