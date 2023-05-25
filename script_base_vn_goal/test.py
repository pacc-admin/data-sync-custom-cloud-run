import requests
import pandas as pd


goal_access_token={'access_token':"7383-QRDX8A6GJKSU9ZW9B6F75FEYRLRLCY4928R546UTKYLJPCMETX2F2NENG5Y258VH-RCCVL89HC23CEWVKHPGUFT5NG2PA2CE8AX2WX9AVNPFXSVT79SR7RGGXJ9D648JK"}

def get_cycles():
    url='https://goal.base.vn/extapi/v1/cycle/list'

    cycles_response=requests.post(url,data=goal_access_token).json()['cycles']
    cycles_paths=[]
    for d in cycles_response:
        cycles_paths.append(d['path'])
    print(cycles_paths)

    return cycles_paths

goal_ids=[]
for path in get_cycles():
    goal_id_cycles=[]
    print(path)
    d={**goal_access_token,**{'path':path}}
    url='https://goal.base.vn/extapi/v1/cycle/get.full'
    response=requests.post(url,data=d).json()
    
    for d in response['goals']:
        goal_id_cycles.append(d['id'])
    print(type(goal_id_cycles))
    goal_ids=goal_ids.append(goal_id_cycles)
    print(type(goal_ids))
print(goal_ids)

#d={**goal_access_token,**{'id':'8969'}}

#a=response['goal']
##df=pd.DataFrame.from_dict(a)
#df=pd.DataFrame(response['cycles'])
#df.to_csv('out.csv')
#print(df)