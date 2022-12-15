import dbconnector
import re
import inflect
p = inflect.engine()
import pandas as pd

lists = { 
          'list4':'tax'
}


for c2,c1 in lists.items():
    s=dbconnector.base_vn_connect(app='hrm',component1=c1,component2=c2)
    c1p=p.plural(c1)
    dataset = pd.DataFrame(s)
    flatten = pd.json_normalize(dataset[c1p])
    print(dataset.head(10))


#import requests
#p={'access_token': '7383-SRGCCB22PNT8Y7A47M9HYQNXUVGFDBWVNQ2BVH3WLQUS2RD83Q5YD4CSB79XXS3G-LKSK5HRBSNPS3235ZQBR5QD92FM5EFALVCWLKHCCK22EXGJ8D2YS8CJVB2HDYYZ8', 'updated_from': 0, 'page': 0}
#url="https://hrm.base.vn/extapi/v1/employee/list"
#raw_output = requests.get(url, params=p).json()