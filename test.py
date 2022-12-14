import dbconnector

query_string='SELECT max(cast(TRAN_DATE as date)) as TRAN_DATE FROM `pacc-raw-data.IPOS_SALE.sale`'

dataframe = dbconnector.bq_pandas(query_string)
a=dataframe['TRAN_DATE'].astype(str).to_list()[0]
print(a)