# CoinGecko Platform Spcecific Price Extractor
A tool that allows you to select a specific platform and return current pricing data timestamped in a dataframe. Works on Python 3.8.1

## Requiements
Make sure you have Pandas installed. Other packages which may or may not be needed can be found in the `requirements.txt`. 

## Set-Up
- Find the plaform ID you need in the `CoinGecko_Platform_List.txt`
### get_contracts Function
 - First argument is a string of the Platform ID from the above `CoinGecko_Platform_List.txt`
 - Second argument is the a boolean value for `is_ethereum_L2`
 - Function will return a list of all the contract addresses for the platform chosen, put this into a variable called `contract_address_list`
 - Example: `contract_address_list = get_contracts('platforms.harmony-shard-0',is_ethereum_L2=True)`

### get_prices Function
- Function takes in three arguments first argument is the contract addresses in a comma seperated list (use the output of the above function)
- The second argument is the same Coingecko Platform ID used in the function above
- Last arguemtn is a boolean value for verbose (true will return marketcap, 24 hr volume, and 24 price change as well as price), if False just price will be returned
- Function will return a dataframe of shaped and timestamped data (UTC)
- Example `df = get_prices(contract_address_list,'platforms.harmony-shard-0',verbose=True)`


You can either work from within python with the dataframe or export the dataframe to csv via `df.to_csv('export_file_name.csv')`
