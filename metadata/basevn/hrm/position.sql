create or replace table `pacc-raw-data.BASEVN_HRM.position`  (
    id string,
    name string,
    code string,
    status string,
    content string,
    objs string,
    promotion_reqs string,
    area_id string,
    type_id string,
    links string,
    image string,
    icon int64,
    last_update string,
    salary_min int64,
    salary_max int64,
    data___io float64,
    salary_strict float64,
    salary_hide float64,
    data_employee_hide float64,
    loaded_date timestamp

)

partition by date(loaded_date)