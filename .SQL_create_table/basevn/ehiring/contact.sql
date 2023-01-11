create or replace table `pacc-raw-data.BASEVN_EHIRING.contact` (
   id string,
   type string,
   hid string,
   token string,
   first_name string,
   last_name string,
   score array<string>,
   sources string,
   source_id string,
   campaigns array<string>,
   tags array<string>,
   phone string,
   changelogs array<string>,
   abs_link string,
   ns_id string,
   image string,
   name string,
   email string,
   title string,
   address string,
   dob string,
   dob_year string,
   gender string,
   stats string,
   content string,
   fields ARRAY<
     STRUCT<
       id string,
       value string,
       display string,
       type string,
       name string,
       placeholder string
     >>, 
   form array<string>,
   candidates ARRAY<
     STRUCT<
       id string,
       name string,
       type string,
       abslink string,
       status_display string,
       codename string,
       owners array<string>,
       creator string,
       candidate_id string,
       candidate_link string,
       scores array<string>,
       since string
     >>,
   candidate ARRAY<
     STRUCT<
       id string,
       name string,
       type string,
       abslink string,
       status_display string,
       codename string,
       owners array<string>,
       creator string,
       candidate_id string,
       candidate_link string,
       scores array<string>,
       since string
     >>,
   files ARRAY<
     STRUCT<
       id string,
       name string,
       url string
     >>,
   since string,
   apply_time string,
   last_update string,
   highlight string,
   loaded_date timestamp
)

partition by date(loaded_date)