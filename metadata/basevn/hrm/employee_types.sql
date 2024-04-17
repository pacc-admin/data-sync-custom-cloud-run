create or replace table `pacc-raw-data.BASEVN_HRM.employee_types` (
    id string,
    name string,
    content string,
    metatype string,
    code string,
    fte string,
    user_id string,
    since string,
    last_update string,
    config_fte string,
    loaded_date timestamp
)

partition by date(loaded_date)
