#!/usr/bin/python3.8
from numpy import float16, float32, float64
import pandas as pd
import numpy as np
import math
import requests
import datetime as dt
import os
from decouple import config
import snowflake.connector as sf
from snowflake.connector.pandas_tools import write_pandas

platform_id = "platforms.ethereum"
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
    
    #Taking the contracts and putting them into a list to set up the price API Query
    contract_address_list = []
    for x in df4[platform_id]:
         contract_address_list.append(x)
    return contract_address_list

contract_address_list = get_contracts(platform_id,is_ethereum_L2=True)

#Creating the API Query, can uncomment out the extended_api_suffix to get market_cap and 24 hour volume, still working on ETL for that
#Syntax for query url is: simple/token_price/platformid/comma seperated list of contracts (created above)/api_suffix
platform_id = platform_id[10:]
api_prefix =  "https://api.coingecko.com/api/v3/simple/token_price/{}?contract_addresses=0x72cb10c6bfa5624dd07ef608027e366bd690048f".format(platform_id)
extended_api_suffix = "&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"
api_suffix = "&vs_currencies=usd"

n = 100
contract_num = len(contract_address_list)
print(contract_num)
print(len(contract_address_list))
column_list = ['address',	'usd',	'usd_24h_change',	'usd_24h_vol',	'usd_market_cap',	'timestamp']
df3 = pd.DataFrame(columns=column_list)

#ETL of the contract address list to remove blanks
while("" in contract_address_list) :
    contract_address_list.remove("")
list_of_contract_address_list=[contract_address_list[i:i + n] for i in range(0, len(contract_address_list), n)]

#Nested list comprehension to loop through list of lists which contain 50 contract adresses so we can create API URL's that are short enough to work with CG API.
#Basically just creating a bunch of smaller API calls instead of one large one with 5k adresses on URL (this doesn't work)
for address_list_trunc in list_of_contract_address_list:
    for y in address_list_trunc:
        api_prefix = api_prefix + "%2C" + y
    api_url = api_prefix + extended_api_suffix

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
    df2 = df2.round({'usd':6,'usd_24h_vol':2,'usd_market_cap':2,'usd_24h_change':2})
    df2["timestamp"] = dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') 
    api_url = ""
    api_prefix =  "https://api.coingecko.com/api/v3/simple/token_price/{}?contract_addresses=0x72cb10c6bfa5624dd07ef608027e366bd690048f".format(platform_id)
    df3 = pd.concat([df2,df3])
    print(len(df3.index))

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


try:

    # convert to a string list of tuples
    df3 = str(list(df2.itertuples(index=False, name=None)))
    # get rid of the list elements so it is a string tuple list
    df3 = df3.replace('[','').replace(']','').replace('None','0').replace('nan','0')
    df3 = df3
    #print(df2)
    # set up execute
    cs.execute(
         """ INSERT INTO """ + "ALL_COINGECKO_USD_PRICES" + """
             VALUES """ + df3 + """
         """)
finally:
    cs.close()
conn.close()