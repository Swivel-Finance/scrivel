#!~/python/scrivel/bin/python

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

# get a filter for the event(s), use the lower-level contract instance itself
initiate_filter = swivel.contract.events.Initiate.createFilter(fromBlock=Web3.toHex(13400000), toBlock='latest')
initiate_logs = initiate_filter.get_all_entries()
# pick out the txs via comprehension
initiate_txs = [log['transactionHash'] for log in initiate_logs]

print(yellow('Initiate event entries: '))
for tx in initiate_txs:
    print(magenta('Transaction Hash: ') + white(Web3.toHex(tx)))

exit_filter = swivel.contract.events.Exit.createFilter(fromBlock=Web3.toHex(13400000), toBlock='latest')
exit_logs = exit_filter.get_all_entries()
# pick out the txs via comprehension
exit_txs = [log['transactionHash'] for log in exit_logs]

print(yellow('Exit event entries: '))
for tx in exit_txs:
    print(magenta('Transaction Hash: ') + white(Web3.toHex(tx)))
