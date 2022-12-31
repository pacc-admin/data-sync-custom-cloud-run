- Below script is used to extract and load data from IPOS CRM server
- First We will use access token provided by IPOS to call API, by following the guidance below:
  https://documenter.getpostman.com/view/2504154/SVYnRLh7?version=latest#2b978dae-942a-458d-bc2f-7e650b326719

- Then, create a temporary table call `_tmp_membership_check` to include following information:
    - membership_id from IPOS sale server
    - latest updated date of memberinformation from `membership_detail` => `update_at`
    - latest voucher created date from `member_vouchers` => `date_created`
    
- Next, we will convert api result to pandas data frame for below dataset:
    - `membership_detail`
    - `member_vouchers`

- We also need to exclude entries which have updated date <= the date in `_tmp_membership_check`:
    - for `membership_detail`, compare with `update_at`
    - for `member_vouchers`, compare with `date_created`

- The last step would be inserting filtered value from previous step to tables in Bigquery and drop tempt table `_tmp_membership_check`
    - In this step, you also need to check errors recorded in the file `errors.txt`, to fix those later

- for detail, refer to package `dbconnector/ipos_crm_flow.py`