import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
from ipos_crm_module import ipos_crm_el

brand='5WINE'
schema=f'IPOS_CRM_{brand}'
table='membership_detail'
column_updated='update_at'

#execute
def __main__():
    with ipos_crm_el(
        brand,
        table,
        schema 
    ) as func:
        func.bq_load()
        
if __name__ == '__main__':
    __main__()