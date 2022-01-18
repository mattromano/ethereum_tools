from importlib.resources import path
import pandas as pd
import time
import requests

df1 = pd.read_csv("token_list.csv")

print(df1.head())
contract_address_list = []

for x in df1['TOKEN_ADDRESS']:
    contract_address_list.append(x)



#print(contract_address_list)

api_prefix =  "https://api.coingecko.com/api/v3/simple/token_price/harmony-shard-0?contract_addresses=0x72cb10c6bfa5624dd07ef608027e366bd690048f"
api_suffix = "&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"
#for y in contract_address_list:
#    api_prefix = api_prefix + "%2C" + y

comma_sep_string = ","

for y in contract_address_list:
    comma_sep_string = comma_sep_string +  y + ","

#print(comma_sep_string) 

coin_list = "https://api.coingecko.com/api/v3/coins/list?include_platform=true"


request_url = api_prefix + api_suffix
request_url = "https://api.coingecko.com/api/v3/simple/token_price/harmony-shard-0?contract_addresses=0x72cb10c6bfa5624dd07ef608027e366bd690048f%2C0x0dc78c79b4eb080ead5c1d16559225a46b580694%2C0x8750f5651af49950b5419928fecefca7c82141e3&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"

#print(request_url)

response = requests.get(coin_list)
response = response.json()
df2 = pd.json_normalize(response)
#df2["platforms"]
df2.to_csv("coinlist.csv")
print(df2.head())
#print(df2["platforms"])
#print(response)

#eth_market_data = eth_price['market_data']['price_change_percentage_1h_in_currency']['usd']
#print(type(eth_market_data))
