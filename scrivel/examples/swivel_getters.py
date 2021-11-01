#!/home/robrobbins/python/scrivel/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from swivel.contracts import Swivel
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
pass the vendor to the constructor of the 'higher-order-contract' (H.O.C) to construct an instance

* contracts are already deployed, use the swivel classes to wrap them via their 'at' method
"""

provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)

swivel= Swivel(vendor)
swivel.at(SWIVEL_ADDRESS)

# start allows colors to work on $WIN
start()

# the HOC should be ready to use now
print(white('Swivel contract at ') + blue(swivel.address) + white(' successfully wrapped'))

"""
getters don't require any additional transaction options to be passed
"""

admin_address = swivel.admin()
print(white('MarketPlace admin address: ') + blue(admin_address))

name = swivel.NAME()
print(white('Name: ') + magenta(name))

verz = swivel.VERSION()
print(white('Version: ') + magenta(verz))

hold = swivel.HOLD()
print(white('Holding period imposed on admin token withdrawals: ') + magenta(str(hold)))

dom = swivel.domain()
print(white('EIP712 Domain: ') + magenta(dom.hex()))

m_place = swivel.market_place()
print(white('MarketPlace Contract associated with this Swivel deployment: ') + magenta(m_place))

fees1 = swivel.fenominator(0)
fees2 = swivel.fenominator(1)
fees3 = swivel.fenominator(2)
fees4 = swivel.fenominator(3)
print(white('Fee structure for this deployment: ') + magenta(str((fees1, fees2, fees3, fees4))))

stop()
