import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../dbconnector")
import ipos_crm_flow

brands=['BGN','5WINE']

for brand in brands:
    ipos_crm_flow.crm_campaigns_insert(brand)