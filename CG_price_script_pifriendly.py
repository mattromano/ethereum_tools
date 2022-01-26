#!/usr/bin/python3.8
from numpy import float16, float32, float64
import pandas as pd
import numpy as np
import math
import requests
import datetime as dt

platform_id = "platforms.harmony-shard-0"
#get_contacts function takes in two arguments, one being the CoinGecko Platform ID and the second is a boolean for if the platform is an ETH L2.
#Function will return a list of all contract addresses on chosen platform which can be used to set up the CoinGecko API Price Query 
def get_contracts(platform_id, is_ethereum_L2: bool):


    #Grabbing all of the contracts available on coingecko and the platforms the exist on
    coin_list = "https://api.coingecko.com/api/v3/coins/list?include_platform=true"
    response = requests.get(coin_list)
    response = response.json()
    df1 = pd.json_normalize(response)
    all_plaform_ids = list(df1.columns)
    all_plaform_ids = all_plaform_ids[3:]
    all_plaform_ids_less_target = [i for i in all_plaform_ids if i != platform_id]

    #keeping eth as plaform if it's an L2
    if is_ethereum_L2 == True:
        all_plaform_ids_less_target = [i for i in all_plaform_ids_less_target if i != 'platforms.ethereum']


    #Isolating to just the Harmony Contracts we need
    df2 = df1.dropna(subset=[platform_id])
    df4 = df2.drop(all_plaform_ids_less_target, axis=1)
    print(df4[platform_id])
    
    #Taking the contracts and putting them into a list to set up the price API Query
    contract_address_list = []
    for x in df4[platform_id]:
         contract_address_list.append(x)
    return contract_address_list

contract_address_list = get_contracts(platform_id,is_ethereum_L2=False)

#Creating the API Query, can uncomment out the extended_api_suffix to get market_cap and 24 hour volume, still working on ETL for that
#Syntax for query url is: simple/token_price/platformid/comma seperated list of contracts (created above)/api_suffix
api_prefix =  "https://api.coingecko.com/api/v3/simple/token_price/harmony-shard-0?contract_addresses=0x72cb10c6bfa5624dd07ef608027e366bd690048f"
extended_api_suffix = "&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"

#api_suffix = "&vs_currencies=usd"
for y in contract_address_list:
   api_prefix = api_prefix + "%2C" + y
api_url = api_prefix + extended_api_suffix
print(extended_api_suffix)

#ETL on the API response to get into address,usd_price,time_stamp
response = requests.get(api_url)
response = response.json()
df2 = pd.json_normalize(response)
df2 = df2.transpose()
df2 = df2.reset_index()
df2[['address', 'price_data']] =  df2['index'].str.split('.',expand=True)
df2 = df2.rename(columns= { 0: "measure"})
df2 = df2.drop(columns=['index'], axis=1)
df2 = df2[['address','price_data','measure']]
df2 = df2.pivot(index='address',columns='price_data',values='measure')
df2 = df2.reset_index()
df2 = df2.drop(columns=['last_updated_at'], axis=1)
df2[['usd', 'usd_24h_change','usd_24h_vol','usd_market_cap' ]] = df2[['usd', 'usd_24h_change','usd_24h_vol','usd_market_cap' ]].astype(float64)
df2 = df2.round({'usd_24h_vol':2,'usd_market_cap':2,'usd_24h_change':2})
#df2.to_csv('test.csv')
print(df2)
df2["timestamp"] = dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
print(df2)

#Writing into the snowflake - need to fix datetime issues. Address & Price work
conn = sf.connect(
    user = config('SF_USERNAME'),
    password = config('SF_PASSWORD'),
    account = config('SF_ACCOUNT'),
    warehouse = config('SF_WAREHOUSE'),
    database = config('SF_DATABASE'),
    schema = config('SF_SCHEMA')
)
cs = conn.cursor()

print(df2)
try:

    # convert to a string list of tuples
    df2 = str(list(df2.itertuples(index=False, name=None)))
    # get rid of the list elements so it is a string tuple list
    df2 = df2.replace('[','').replace(']','').replace('None','0').replace('nan','0')
    df2 = df2
    #print(df2)
    # set up execute
    cs.execute(
         """ INSERT INTO """ + "TOKEN_USD_PRICES_MR" + """
             VALUES """ + df2 + """

         """)
finally:
    cs.close()
conn.close()
