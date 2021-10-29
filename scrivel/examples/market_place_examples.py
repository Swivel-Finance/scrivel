#!/home/robrobbins/python/scrivel/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from swivel.contracts import MarketPlace
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

# the HOC should be ready to use now
print('MarketPlace at {} successfully wrapped'.format(market_place.address))

"""
getters don't require any additional transaction options to be passed
"""

admin_address = market_place.admin()
print('MarketPlace admin address: {}'.format(admin_address))

swivel_address = market_place.swivel()
print('MarketPlace swivel address: {}'.format(swivel_address))

market = market_place.markets(DAI_UNDERLYING, DAI_MATURITY)
print('DAI Market maturing on {}: {}'.format(DAI_MATURITY, market))
