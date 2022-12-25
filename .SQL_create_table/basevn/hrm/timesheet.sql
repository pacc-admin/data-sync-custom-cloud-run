create or replace table `pacc-raw-data.BASEVN_HRM.timesheet`  (
    id string,
    metatype string,
    df string,
    owners string,
    name string,
    timezone string,
    code string,
    shifts string,
    working_days string,
    status string,
    num_shifts string,
    points_per_day string,
    hours_per_day string,
    user_id string,
    since string,
    last_update string,
    type string,
    eba int64,
    config_type string,
    config_checkin_gap string,
    config_checkout_gap string,
    config_required_checkout string,
    loaded_date timestamp

)

partition by date(loaded_date)