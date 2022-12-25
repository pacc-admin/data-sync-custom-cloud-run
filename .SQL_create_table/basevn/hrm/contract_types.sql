create or replace table `pacc-raw-data.BASEVN_HRM.contract_types` (
    id string,
    name string,
    content string,
    metatype string,
    followers string,
    form string,
    since string,
    creator_id string,
    files string,
    is_probation int64,
    tax_id int64,
    insurance_id int64,
    config_probation float64,
    loaded_date timestamp
)

partition by date(loaded_date)
