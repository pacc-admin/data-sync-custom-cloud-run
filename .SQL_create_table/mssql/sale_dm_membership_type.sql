create or replace table `pacc-raw-data.IPOS_SALE.dm_membership_type` (
    membership_type_id string,
    membership_type_name string,
    active int64,
    user_id string,
    workstation_id int64,
    membership_type_parent_id string,
    point_to_amount float64,
    is_once int64
)