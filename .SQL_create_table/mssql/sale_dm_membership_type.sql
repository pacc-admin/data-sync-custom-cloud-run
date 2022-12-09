create or replace table `pacc-raw-data.IPOS_SALE.dm_membership_type` (
    MEMBERSHIP_TYPE_ID string,
    MEMBERSHIP_TYPE_NAME string,
    ACTIVE INT64,
    USER_ID string,
    WORKSTATION_ID int64,
    MEMBERSHIP_TYPE_PARENT_ID string,
    POINT_TO_AMOUNT float64,
    IS_ONCE int64
)