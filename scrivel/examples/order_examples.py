#!<your_path_here>/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3

from scrivel.helpers.orders import order_key, new_order
from scrivel.constants import(
    PUB_KEY,
    DAI_UNDERLYING,
    DAI_MATURITY,
    HTTP_PROVIDER,
    SWIVEL_ADDRESS,
    NETWORK_ID,
)

from scrivel.helpers.colors import(
    start,
    stop,
    cyan,
    white,
    red,
)

start()

# unique order keys are generated like so
uniq_key = order_key(PUB_KEY)
print(white('An order key: ') + cyan(uniq_key.hex()))

# timestamps are used, so consecutive keys should vary accordingly
uniq_key = order_key(PUB_KEY)
print(white('Another order key: ') + cyan(uniq_key.hex()))

# you can get a new, empty order with a unique key ready to be hydrated via new_order.
# with this you could then individually assign the key:vals -> my_order['vault'] = True etc...
my_order = new_order(PUB_KEY)
print(white('An empty order: ') + cyan(str(my_order)))

# you can also pre-hydrate the rest of the order keys by passing them (all or some) as keyword args
my_other_order = new_order(PUB_KEY, underlying=DAI_UNDERLYING, maturity=DAI_MATURITY, vault=False, exit=True,
    principal=10000000000000000000, premium=1000000000000000000, expiry=1636563532)
print(white('A prefilled order: ') + cyan(str(my_other_order)))

# orders are signed via the swivel vendor class (assure that you have exported your PRIVATE_KEY to this term session)
provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)
# we'll use rinkeby chainId and the rinkeby deployed swivel contract as the verifying address
sig = vendor.sign_order(my_other_order, NETWORK_ID, SWIVEL_ADDRESS)
print(white('An order signature: ') + cyan(sig))

# NOTE see /orders/place_order for posting a signed order to the swivel api, and /orders/cancel_order for well, cancelling

stop()
