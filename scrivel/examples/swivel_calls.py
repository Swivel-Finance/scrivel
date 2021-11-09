#!<your_path_here>/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from swivel.contracts import Swivel
from swivel.helpers import call

from scrivel.helpers.colors import(
    start,
    stop,
    yellow,
    blue,
    magenta,
    white,
)

from scrivel.constants import(
    HTTP_PROVIDER,
    PUB_KEY,
    SWIVEL_ADDRESS,
)

"""
calls being any call which is a .call() vs a .transact() type. getters which do not incur any cost
"""

provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)

# instantiate a Higher Order Contract with the vendor
swivel= Swivel(vendor)
# wrap the deployed contract instance via the H.O.C `at` method
swivel.at(SWIVEL_ADDRESS)

# start allows colors to work on $WIN
start()

# the HOC should be ready to use now
print(white('Swivel contract at ') + blue(swivel.address) + white(' successfully wrapped'))

# getters don't require any additional transaction options to be passed
admin_address = call(swivel.admin())
print(white('MarketPlace admin address: ') + blue(admin_address))

name = call(swivel.NAME())
print(white('Name: ') + magenta(name))

verz = call(swivel.VERSION())
print(white('Version: ') + magenta(verz))

hold = call(swivel.HOLD())
print(white('Holding period imposed on admin token withdrawals: ') + magenta(str(hold)))

dom = call(swivel.domain())
print(white('EIP712 Domain: ') + magenta(dom.hex()))

m_place = call(swivel.market_place())
print(white('MarketPlace Contract associated with this Swivel deployment: ') + magenta(m_place))

fees1 = call(swivel.fenominator(0))
fees2 = call(swivel.fenominator(1))
fees3 = call(swivel.fenominator(2))
fees4 = call(swivel.fenominator(3))
print(white('Fee structure for this deployment: ') + magenta(str((fees1, fees2, fees3, fees4))))

stop()
