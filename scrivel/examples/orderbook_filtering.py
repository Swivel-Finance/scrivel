import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))
from sys import exit


from scrivel.helpers.http import (
    orderbook,
)

# Market
underlying = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa" # The underlying token address
maturity = float(1669957199) # The Swivel market maturity in unix
decimals = float(18) # The decimals of the underlying token
networkString = "rinkeby"

if networkString == "mainnet":
    network = 1
    swivelAddress = "0x3b983B701406010866bD68331aAed374fb9f50C9"
elif networkString == "rinkeby":
    network = 4
    swivelAddress = "0x4ccD4C002216f08218EdE1B13621faa80CecfC98"
elif networkString == "kovan":
    network = 42
    swivelAddress = "0x301292f76885b5a20c7dbd0e06F093E9D4e5fA3F"
else:
    print("Invalid network")
    exit(1)


orderbook = orderbook(underlying, 1669957199, 25, network)
receivingPremium = []
payingPremium = []
for i in orderbook:
    if i == "receivingPremium":
        receivingPremium = orderbook[i]

    if i == "payingPremium":
        payingPremium = orderbook[i]

    