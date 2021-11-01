#!/home/robrobbins/python/scrivel/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from swivel.contracts import MarketPlace
from scrivel.helpers.colors import(
    start,
    stop,
    yellow,
    blue,
    green,
    cyan,
    red,
)

from scrivel.constants import(
    HTTP_PROVIDER,
    PUB_KEY,
    MARKET_PLACE_ADDRESS,
    DAI_UNDERLYING,
    DAI_MATURITY,
)

"""
pass the vendor to the constructor of the 'higher-order-contract' (H.O.C) to construct an instance

* contracts are already deployed, use the swivel classes to wrap them via their 'at' method
"""

provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)

market_place = MarketPlace(vendor)
market_place.at(MARKET_PLACE_ADDRESS)

# start allows colors to work on $WIN
start()

# the HOC should be ready to use now
print(yellow('MarketPlace at ') + blue(market_place.address) + yellow(' successfully wrapped'))

"""
getters don't require any additional transaction options to be passed
"""

admin_address = market_place.admin()
print(yellow('MarketPlace admin address: ') + blue(admin_address))

swivel_address = market_place.swivel()
print(yellow('MarketPlace swivel address: ') + blue(swivel_address))

market = market_place.markets(DAI_UNDERLYING, DAI_MATURITY)
print(yellow('DAI Market maturing on: ') + blue(str(DAI_MATURITY)) + cyan(str(market)))

c_token_address = market_place.c_token_address(DAI_UNDERLYING, DAI_MATURITY)
print(yellow('DAI Market Compound token address: ') + blue(c_token_address))

matured = market_place.mature(DAI_UNDERLYING, DAI_MATURITY)
print(yellow('DAI Market matured? ') + red(str(matured)))

# return the console to normal
stop()
