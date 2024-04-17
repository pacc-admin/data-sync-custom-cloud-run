create table `pacc-raw-data.GOOGLE_SHEETS.daily_sale_targets` (
  
  sale_index	STRING,
  growth_rate	STRING,
  branch_picker	STRING,
  forecasted_date	STRING,
  historical_date	STRING,
  forecasted_net_sales STRING,
  historical_net_sales STRING,
  loaded_date timestamp
)

partition by date(loaded_date)