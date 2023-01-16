create or replace table `pacc-raw-data.BASEVN_CHECKIN.checkin_logs` (         
  id string,              
  user_id string,         
  employee_id string,     
  date string,            
  month_index string,     
  timesheet_id string,
  computed_is_late float64,
  computed_day_point float64,
  computed_sum_minute_late float64,
  computed_sum_late float64,
  computed_shift_info array < struct <
      shift_point float64,
      is_late int64,
      late int64,
      min_early int64,
      deduction int64,
      not_checkout int64,
      shift_index int64,
      type_id string,
      metatype string,
      assigned_shift_id int64
  >>,       
  finalized_is_late float64,
  finalized_day_point float64,
  finalized_sum_minute_late float64,
  finalized_sum_late float64,
  finalized_shift_info array < struct <
      shift_point float64,
      is_late int64,
      late int64,
      min_early int64,
      deduction int64,
      not_checkout int64,
      shift_index int64,
      type_id string,
      metatype string,
      assigned_shift_id int64
  >>,      
  logs string,         
  hid string,             
  token string,           
  type string,            
  stats_comments int64,           
  loaded_date timestamp
)

partition by date(loaded_date)


  logs array < struct <
    ip  STRING,
    client_id STRING,
    office_id STRING,
    time int64,
    metatype string,
    lat  string,
    lng  string,
    img string,
    checkout int64,
    note string,
    files ARRAY<int64> ,
    content string,
    photo string
  >>,      