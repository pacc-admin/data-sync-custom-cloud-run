create or replace table `pacc-raw-data.BASEVN_HRM.legals`  (
    id string,
    employee_id string,
    tax_no string,
    inso_no string,
    inso_place string,
    personal_deduction string,
    ssn_no string,
    ssn_place string,
    ssn_date string,
    date string,
    loaded_date timestamp
)

partition by date(loaded_date)