create or replace table `pacc-raw-data.BASEVN_HRM.tax` (
    id string,
    type string,
    metatype string,
    code string,
    user_id string,
    username string,
    name string,
    content string,
    since string,
    last_update string,
    status string,
    color string,
    percent string,
    eba string,
    config_percent string,
    loaded_date timestamp
)

partition by date(loaded_date)
