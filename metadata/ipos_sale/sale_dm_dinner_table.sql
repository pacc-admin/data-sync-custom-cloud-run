create table `pacc-raw-data.IPOS_SALE.dm_dinner_table` (
    UNIQUE_KEY bytes,
    DATA_SOURCE string,
    PR_KEY	float64,
    DINNER_TABLE_ID	string,
    AREA_ID	string,
    DINNER_TABLE_NAME	string,
    DINNER_TABLE_TYPE	int64,
    ENABLE	int64,
    ACTIVE	int64,
    USER_ID	string,
    WORKSTATION_ID	int64,
    WHOS	string,
    LOADED_DATE timestamp
)
