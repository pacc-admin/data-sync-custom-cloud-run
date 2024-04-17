create or replace table `pacc-raw-data.BASEVN_HRM.area` (
    id string,
    name string,
    code string,
    content string,
    metatype string,
    type string,
    since string,
    last_update string,
    loaded_date timestamp
)

partition by date(loaded_date)