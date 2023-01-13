create or replace table `pacc-raw-data.BASEVN_EHIRING.opening` (
   id string,
   name string,
   codename string,
   content string,
   starred string,
   dept_id string,
   salary string,
   period string,
   status string,
   metatype string,
   num_positions string,
   company_name string,
   office_name string,
   offices array<string>,
   locations array<int64>,
   deadline string,
   stime string,
   etime string,
   talent_pool_id string,
   since string,
   last_update string,
   loaded_date timestamp
)

partition by date(loaded_date)