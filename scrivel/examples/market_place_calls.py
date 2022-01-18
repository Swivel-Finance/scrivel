# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from swivel.contracts import MarketPlace
from swivel.helpers import call

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
calls being any call which is a .call() vs a .transact() type. getters which do not incur any cost
"""

provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)

# instantiate a Higher Order Contract with the vendor
market_place = MarketPlace(vendor)
# wrap the deployed contract instance via the H.O.C `at` method
market_place.at(MARKET_PLACE_ADDRESS)

# start allows colors to work on $WIN
start()

# the HOC should be ready to use now
print(yellow('MarketPlace at ') + blue(market_place.address) + yellow(' successfully wrapped'))

# getters don't require any additional transaction options to be passed
admin_address = call(market_place.admin())
print(yellow('MarketPlace admin address: ') + blue(admin_address))

swivel_address = call(market_place.swivel())
print(yellow('MarketPlace swivel address: ') + blue(swivel_address))

market = call(market_place.markets(DAI_UNDERLYING, DAI_MATURITY))
print(yellow('DAI Market maturing on: ') + blue(str(DAI_MATURITY)) + cyan(str(market)))

c_token_address = call(market_place.c_token_address(DAI_UNDERLYING, DAI_MATURITY))
print(yellow('DAI Market Compound token address: ') + blue(c_token_address))

# markets are considered mature when their maturityRate > 0 (maturity rate is index 3 in the list of 4)
matured = market[3] > 0
print(yellow('DAI Market matured? ') + red(str(matured)))

# return the console to normal
stop()
