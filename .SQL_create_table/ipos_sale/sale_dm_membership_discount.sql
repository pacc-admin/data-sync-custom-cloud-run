create or replace table `pacc-raw-data.IPOS_SALE.dm_membership_discount` (
    MEMBERSHIP_TYPE_ID	string,
    MEMBERSHIP_TYPE_NAME	string,
    ACTIVE	int64,
    USER_ID	string,
    WORKSTATION_ID	int,
    MEMBERSHIP_TYPE_PARENT_ID	string,
    POINT_TO_AMOUNT	float64,
    IS_ONCE	int64,
    LOADED_DATE timestamp
)
