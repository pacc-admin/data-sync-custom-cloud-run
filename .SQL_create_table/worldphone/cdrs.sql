create or replace table `pacc-raw-data`.WORLDFONE.cdrs (
    calldate string,
    src string,
    dst string,
    queue string,
    disposition string,
    duration int64,
    billsec int64,
    holdtime int64,
    waitingtime int64,
    uniqueid string,
    accountcode string,
    did_number string,
    direction string,
    carrier string,
    loaded_date timestamp
)
partition by (date(loaded_date))