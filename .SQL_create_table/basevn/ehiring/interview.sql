create or replace table `pacc-raw-data.BASEVN_EHIRING.interview` (
   id string,
   name string,
   user_id string,
   username string,
   metatype string,
   time string,
   date int64,
   est_duration int64,
   token string,
   last_ping int64,
   candidate_id string,
   candidate_export array<
     struct<
       id string,
       name string,
       type string,
       phone string,
       email string,
       title string,
       link string
     >>,
   candidate_name string,
   candidate_phone string,
   candidate_email string,
   candidate_title string,
   followers array<string>,
   opening_id string,
   opening_name string,
   msgthread_id string,
   status string,
   confirmed string,
   interacted int64,
   hr_set_cf int64,
   questions string,
   sendmail string,
   acl string,
   location string,
   starred string,
   loaded_date timestamp
)

partition by date(loaded_date)