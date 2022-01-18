from importlib.resources import path
import pandas as pd
import time
import requests

request_url = "https://api.coingecko.com/api/v3/simple/token_price/harmony-shard-0?contract_addresses=0x72cb10c6bfa5624dd07ef608027e366bd690048f%2C0x0dc78c79b4eb080ead5c1d16559225a46b580694%2C0x8750f5651af49950b5419928fecefca7c82141e3&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"

coin_list = "https://api.coingecko.com/api/v3/coins/list?include_platform=true"
#print(request_url)

response = requests.get(coin_list)
response = response.json()
df2 = pd.json_normalize(response)
df2.head()

df3 = df2.dropna(subset = ["platforms.harmony-shard-0"])

df4 = df3.drop(
    [
 'platforms.polygon-pos',
 'platforms.avalanche',
 'platforms.binance-smart-chain',
 'platforms.fantom',
 'platforms.xdai',
 'platforms.kardiachain',
 'platforms.moonriver',
 'platforms.tron',
 'platforms.huobi-token',
 'platforms.sora',
 'platforms.polkadot',
 'platforms.chiliz',
 'platforms.komodo',
 'platforms.cardano',
 'platforms.optimistic-ethereum',
 'platforms.ardor',
 'platforms.qtum',
 'platforms.stellar',
 'platforms.arbitrum-one',
 'platforms.cronos',
 'platforms.solana',
 'platforms.osmosis',
 'platforms.algorand',
 'platforms.celo',
 'platforms.aurora',
 'platforms.eos',
 'platforms.neo',
 'platforms.terra',
 'platforms.Bitcichain',
 'platforms.waves',
 'platforms.okex-chain',
 'platforms.',
 'platforms.ronin',
 'platforms.icon',
 'platforms.smartbch',
 'platforms.nem',
 'platforms.bitshares',
 'platforms.binancecoin',
 'platforms.iotex',
 'platforms.fuse',
 'platforms.kucoin-community-chain',
 'platforms.hoo',
 'platforms.zilliqa',
 'platforms.klay-token',
 'platforms.boba',
 'platforms.secret',
 'platforms.tezos',
 'platforms.fusion-network',
 'platforms.xrp',
 'platforms.cosmos',
 'platforms.telos',
 'platforms.gochain',
 'platforms.vechain',
 'platforms.bitcoin-cash',
 'platforms.tomochain',
 'platforms.nuls',
 'platforms.metis-andromeda',
 'platforms.elrond',
 'platforms.stratis',
 'platforms.kava',
 'platforms.kusama',
 'platforms.omni',
 'platforms.metaverse-etp',
 'platforms.nxt',
 'platforms.enq-enecuum',
 'platforms.ontology',
 'platforms.factom',
 'platforms.wanchain',
 'platforms.rootstock',
 'platforms.openledger',
 'platforms.vite']
 ,axis=1
)