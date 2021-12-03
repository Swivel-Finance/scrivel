#!<your_path_here>/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from swivel.contracts import VaultTracker
from swivel.helpers import call

from scrivel.helpers.colors import(
    start,
    stop,
    green,
    blue,
    cyan,
    white,
    red,
)

from scrivel.constants import(
    HTTP_PROVIDER,
    PUB_KEY,
    MARKET_PLACE_ADDRESS,
    DAI_UNDERLYING,
    DAI_MATURITY,
    VAULT_ADDRESS,
)

"""
pass the vendor to the constructor of the 'higher-order-contract' (H.O.C) to construct an instance

* contracts are already deployed, use the swivel classes to wrap them via their 'at' method
"""

provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)

tracker = VaultTracker(vendor)
# you can instantiate a stand alone VaultTracker with the market.vaultAddr
tracker.at(VAULT_ADDRESS)

# start allows colors to work on $WIN
start()

# the HOC should be ready to use now
print(cyan('Vault Tracker contract at ') + green(tracker.address) + cyan(' successfully wrapped'))

# the vault tracker admin should be the marketplace contract
admin_address = call(tracker.admin())
print(cyan('VaultTracker admin address: ') + green(admin_address))
print(cyan('Same as the MarketPlace Contract address: ') + green(MARKET_PLACE_ADDRESS))

c_token_address = call(tracker.c_token_address())
print(cyan('VaultTracker Compound token address: ') + green(c_token_address))

swivel_address = call(tracker.swivel())
print(cyan('Swivel Contract address associated with this Vault: ') + green(swivel_address))

# considered matured if maturityRate > 0
rate = call(tracker.maturity_rate())
print(cyan('Vault matured? ') + red(str(rate > 0)))

maturity = call(tracker.maturity())
print(cyan('Vault maturity ') + green(str(maturity)))

owner_vault = call(tracker.vaults(PUB_KEY))
print(cyan('Vault belonging to ') + green(PUB_KEY) + ', ' + blue(str(owner_vault)))

balances = call(tracker.balances_of(PUB_KEY))
print(cyan('Balances for ') + green(PUB_KEY) + ', ' + blue(str(balances)))

# you can convert the large wei numbers to ETH via web3's converters
print(cyan('Vault notional: ') + green(str(vendor.instance.fromWei(balances[0], 'ether'))) + blue(' ETH'))
print(cyan('Vault redeemable: ') + green(str(vendor.instance.fromWei(balances[1], 'ether'))) + blue(' ETH'))
stop()
