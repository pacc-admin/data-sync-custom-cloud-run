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
    is_probation string,
    tax_id string,
    insurance_id string,
    config_probation string,
    loaded_date timestamp
)

partition by date(loaded_date)
