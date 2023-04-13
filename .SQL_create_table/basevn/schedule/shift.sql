create or replace table `pacc-raw-data`.BASEVN_SCHEDULE.shift (
  id string,
  timesheet_id string,
  employee_id string,
  user_id string,
  date string,
  s_time string,
  e_time string,
  earliest_ci string,
  latest_ci string,
  earliest_co string,
  latest_co string,
  break string,
  standard_point string,
  type_id string,
  jobsite_id string,
  slot string,
  color string,
  note string,
  published string,
  data string,
  since string,
  last_update string,
  creator_id string,
  type_name string,
  jobsite_name string,
  loaded_date timestamp

)

partition by date(loaded_date)