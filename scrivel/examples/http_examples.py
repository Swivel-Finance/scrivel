#!<your_path_here>/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3

from scrivel.helpers.orders import new_order, stringify, parse

from scrivel.helpers.http import (
    markets,
    last_trade,
    orders,
    order,
    limit_order,
)

from scrivel.constants import(
    PUB_KEY,
    DAI_UNDERLYING,
    DAI_MATURITY,
    HTTP_PROVIDER,
    SWIVEL_ADDRESS,
)

from scrivel.helpers.colors import(
    start,
    stop,
    blue,
    white,
)

start()

# get all markets
print(white('All Markets: ') + blue(str(markets())))

# get only active markets
print(white('Active Markets: ') + blue(str(markets(status='active'))))

# we can look at the last recorded trade activity via
trade = last_trade(DAI_UNDERLYING, DAI_MATURITY)
# note the parsed data is in a list...
print(white('Last trade for specified market: ') + blue(str(trade)))

# you can grab that price
print(white('Latest price (via last trade): ') + blue(trade['price']))

# a user (pub_key) may view their active orders
my_orders = orders(DAI_UNDERLYING, DAI_MATURITY, PUB_KEY)
print(white('Active Orders by maker: ') + blue(str(my_orders)))

# use a specific order key to get that order via the order helper
api_order = order('0x3a9586f0dc571d330f0b014e5fbd618e4c169e294a3aeb7a3cdf1ea7c53e7496')

# orders from the api are "stringified", use the parse helper to prepare one for use with H.O.C methods
parsed = parse(api_order['order'])
print(white('Parsed order: ') + blue(str(parsed)))
# the signature and other meta properties are available...
api_order_signature = api_order['meta']['signature']
print(white('API Order signature: ') + blue(api_order_signature))

# a user may view orders that are not active by specifiying a status (see helpers/http non_active_order_status)
# NOTE: at present these will be included with active orders, this is slated to change in an upcoming API version...
my_insolvent_orders = orders(DAI_UNDERLYING, DAI_MATURITY, PUB_KEY, status='insolvent')
print(white('Insolvent Orders by maker: ') + blue(str(my_insolvent_orders)))

# placing a limit order
my_order = new_order(PUB_KEY, underlying=DAI_UNDERLYING, maturity=DAI_MATURITY, vault=False, exit=True,
    principal=12000000000000000000, premium=1100000000000000000, expiry=1639790700)

# you may want to keep the key in order to reference the order...
my_order_key = my_order['key'].hex()
print(white('New Order Key: ') + blue(my_order_key))

provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)

sig = vendor.sign_order(my_order, 4, SWIVEL_ADDRESS)
print(white('New Order signature: ') + blue(sig))

# we leave this commented out to prevent spamming the orderbook

# NOTE: use the stringify helper to match what the api expects
# status, reason = limit_order(stringify(my_order), sig) 
# print(white('API Limit Order Response: ') + blue(str(status)) + white(', ') + blue(reason))

stop()
