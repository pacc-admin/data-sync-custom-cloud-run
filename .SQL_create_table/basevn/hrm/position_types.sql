create or replace table `pacc-raw-data.BASEVN_HRM.position_types` (
    id string,
    user_id string,
    name string,
    content string,
    objs string,
    promotion_reqs string,
    since string,
    last_update string,
    color string,
    type string,
    icon string,
    fill string,
    loaded_date timestamp
)

partition by date(loaded_date)
