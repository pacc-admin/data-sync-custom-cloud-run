create or replace table `pacc-raw-data.BASEVN_HRM.insurance` (
    id string,
    type string,
    metatype string,
    user_id string,
    username string,
    name string,
    code string,
    content string,
    since string,
    last_update string,
    percent_company string,
    percent_employee string,
    status string,
    color int64,
    eba int64,
    loaded_date timestamp
)

partition by date(loaded_date)
