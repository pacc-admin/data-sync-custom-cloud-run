create or replace table `pacc-raw-data.BASEVN_EHIRING.pool` (
    id string,
    hid string,
    token string,
    name string,
    content string,
    owners string,
    followers string,
    path string,
    stats string,
    username string,
    visible string,
    total string,
    metatype string,
    managed int64,
    user_id string,
    since string,
    loaded_date timestamp
)

partition by date(loaded_date)