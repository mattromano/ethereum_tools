from numpy import float16, float32, float64
import pandas as pd
import numpy as np
import requests
import datetime as dt


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


    print(df1.head())
    #Isolating to just the Harmony Contracts we need
    df2 = df1.dropna(subset=[platform_id])
    df4 = df2.drop(all_plaform_ids_less_target, axis=1)
    print(df4[platform_id])
    
    #Taking the contracts and putting them into a list to set up the price API Query
    contract_address_list = []
    for x in df4[platform_id]:
         contract_address_list.append(x)
    return contract_address_list

contract_address_list = get_contracts('platforms.harmony-shard-0',is_ethereum_L2=True)

#get_prices functions takes in three arguments, the contract addresses in a comma seperated list, the Coingecko Platform ID, and a boolean 
#value for verbose (true will return marketcap, 24 hr volume, and 24 price change as well as price)
#The function returns a DataFrame with the data formatted and timestamped 
def get_prices(contract_address_list, platform_id, verbose: bool):
    #Creating the API Query
    #Syntax for query url is: simple/token_price/platformid/comma seperated list of contracts (created above)/api_suffix
    platform_id = platform_id[10:]
    api_prefix =  "https://api.coingecko.com/api/v3/simple/token_price/{}?contract_addresses=0x72cb10c6bfa5624dd07ef608027e366bd690048f".format(platform_id)
    extended_api_suffix = "&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"
    api_suffix = "&vs_currencies=usd"

    #if verbose option is chosen it will include marketcap, 24 hr volume, and 24 price change, if flase then just USD price
    for y in contract_address_list:
        if verbose == True:
            api_prefix = api_prefix + "%2C" + y
            api_url = api_prefix + extended_api_suffix
        else:
            api_prefix = api_prefix + "%2C" + y
            api_url = api_prefix + api_suffix

    #ETL on the API response to get into address,usd_price,time_stamp
    if verbose == True:
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
        df2["timestamp"] = dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return df2
    else:
        response = requests.get(api_url)
        response = response.json()
        df2 = pd.json_normalize(response)
        df2 = df2.transpose()
        df2 = df2.reset_index()
        df2[['address', 'price_data']] =  df2['index'].str.split('.',expand=True)
        df2 = df2.drop(columns=['index','price_data'], axis=1)
        df2 = df2.rename(columns= {0: "usd_price"})
        df2['address'] = df2["address"].str[:42]
        df2["timestamp"] = dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return df2

df = get_prices(contract_address_list,'platforms.harmony-shard-0',verbose=True)
