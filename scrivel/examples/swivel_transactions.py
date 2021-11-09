#!/home/robrobbins/python/scrivel/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from swivel.contracts import Swivel
from scrivel.helpers.http import order
from scrivel.helpers.orders import parse

from scrivel.helpers.colors import(
    start,
    stop,
    magenta,
    white,
)

from scrivel.constants import(
    HTTP_PROVIDER,
    PUB_KEY,
    SWIVEL_ADDRESS,
)

"""
transaction types do incur cost and should have, at least, a { 'gas': xxx } transaction opts dict passed to them
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
print(magenta('Swivel contract at ') + white(swivel.address) + magenta(' successfully wrapped'))

# get a specific order to fill / cancel
api_order = order('0xb0b92dff11480b108d04a69fc0ca6ba27c279b982205d762b0ba7da843652748')
# orders from the api are "stringified", use the parse helper to prepare one for use with H.O.C methods
parsed = parse(api_order['order'])
# the signature and other meta properties are available...
sig = api_order['meta']['signature']
print(white(sig))

# contract abi type tuple[] expectation is actually dict[] (or a tuple of dicts)

# NOTE: assure you have exported PRIVATE_KEY to this terminal session

orders = (parsed, )
amounts = (150000000, )
sigs = (sig, )

# use the vendor.send convenience method to sign a transaction offline and broadcast it
# first, however, include the appropriate tx_opts (from will be added for you by the vendor)
tx_opts = { 'chainId': 4 }

# all of swivel's H.O.C methods return a tuple that consists of (web3_transactable, tx_options).
# many helpers (call, transact, send etc..) expect this tuple as an argument. However, you will often
# want the args yourself first to do other things
txable, opts = swivel.initiate(orders, amounts, sigs, opts=tx_opts)
# you can then pass them as a tuple of 2 to whichever method expects it...

# you can omit 'gas' from tx_opts and allow web3 to estimate the gas for you. of course, you can
# include 'gas' and any other valid `transaction` properties manually. if you would like to see
# the gas estimate (and gas price) before hand use the swivel vendor to do so
gas_estimate, gas_price = vendor.estimate_gas((txable, opts))

# interestingly the gas estimate and gas price are _already_ present in that produced dictionary
print(white('Built Tx gas estimate: ') + magenta(str(gas_estimate)))
print(white('Built Tx gas price: ') + magenta(str(gas_price)))

# the vendor.send method expects the args tuple from any H.O.C transactional method them like so
# NOTE: commented out to prevent spamming the contract
# tx_hash = vendor.send((txable, opts))
# NOTE that if you didnt get the args tuple ahead of time for manipulation, you can just wrap the whole thing...
# tx_hash = vendor.send(swivel.initiate(orders, amounts, sigs, opts=tx_opts))
# print(white('Tx hash for initiate: ') + magenta(str(tx_hash)))

# Web3 static wait_for... method assures mining has completed...
# tx_rcpt = vendor.instance.eth.wait_for_transaction_receipt(tx_hash)
# print(white('Tx receipt for initiate: ') + magenta(str(tx_rcpt)))

# cancel an order...
# tx_hash = vendor.send(swivel.cancel(parsed, sig, {'chainId': 4}))
# print(white('Tx hash for cancel: ') + magenta(str(tx_hash)))

# tx_rcpt = Web3.eth.wait_for_transaction_receipt(tx_hash)
# print(white('Tx receipt for cancel: ') + magenta(str(tx_rcpt)))

stop()
