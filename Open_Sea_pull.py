import requests
import math
import json
import pandas as pd

contract_address = input('Please Enter Contract Address: ')
listing_count = int(input('Please Enter the Amount of Listings: '))

url = "https://api.opensea.io/api/v1/assets"
responselist = []
#def open_sea_API_call(contract_address, listing_count): 
count = math.ceil(listing_count / 50)
offset = 0
while count > 0:
    querystring = {"order_direction":"desc","offset":str(offset),"limit":"50", "asset_contract_address":contract_address}
    response = requests.request("GET", url, params=querystring)
    responselist.append(json.loads(response.text))
    offset = offset + 50
    count = count - 1
    print(count)
    data = responselist
    df1 = pd.json_normalize(data, 'assets',max_level=0)
    df1.to_csv(f'Open_Sea_{contract_address}_{listing_count}.csv')
print('CSV has been exported to current path')
