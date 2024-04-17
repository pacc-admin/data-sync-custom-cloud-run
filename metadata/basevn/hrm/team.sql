create or replace table `pacc-raw-data.BASEVN_HRM.team`  (
    id string,
    name string,
    code string,
    area_id string,
    dept_id string,
    content string,
    metatype string,
    owners string,
    watchers string,
    followers string,
    creator_id string,
    since string,
    last_update string,
    color string,
    loaded_date timestamp

)

partition by date(loaded_date)