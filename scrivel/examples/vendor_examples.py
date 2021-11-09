#!<your_path_here>/bin/python

# this is not a package, so we need to insert scrivel into the path
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from scrivel.constants import HTTP_PROVIDER, PUB_KEY

"""
Swivel.py exposes a W3 class that encapsulates an instance of web3.py.
Instantiate Web3 with your provider and pass that to the W3 class to use.

* create an instance of a Web3 Provider
* pass your public key to the constructor (along with the provider). this assures the correct default account is used
* the vendor keeps the low level web3 reference at 'vendor.instance'
"""

# TODO we can provide a convenience methods for the various cases on the W3 class..
provider = Web3.HTTPProvider(HTTP_PROVIDER)
vendor = W3(provider, PUB_KEY)
# the vendor should have your pub key set
print('Vendor default account {}'.format(vendor.account))
print('Vendor is connected to provider: {}'.format(vendor.instance.isConnected())) # the mixing of camel-case is hella confusing...
