import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))

from web3 import Web3
from swivel.vendors import W3
from time import sleep
from sys import exit
import time
import datetime
import math

from scrivel.helpers.orders import new_order, stringify, parse

from scrivel.helpers.http import (
    markets,
    last_trade,
    orders,
    order,
    limit_order,
)

from scrivel.constants import(
    HTTP_PROVIDER,
    SWIVEL_ADDRESS,
)

from scrivel.helpers.colors import(
    blue,
    white,
)

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def fetchPrice(underlying, maturity) -> float:
    trade = last_trade(underlying, maturity)
    return trade['price']

def simplestMarketMake(underlying, maturity, range, amount, expiryLength):

    price = fetchPrice(underlying, maturity)
    upperBound = price + (price*(range/100))
    lowerBound = price - (price*(range/100))

    safeAmount = amount * .95
    
    splitAmount = safeAmount / 2

    upperPrincipal = truncate(splitAmount,4)
    upperPremium = truncate((splitAmount*upperBound),4)

    lowerPrincipal = truncate(splitAmount/lowerBound),4)
    lowerPremium = truncate(splitAmount,4)

    expiry = datetime.datetime.now() + expiryLength 

    upperOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=maturity, vault=True, exit=True, principal=upperPrincipal, premium=upperPremium, expiry=expiry)

    lowerOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=maturity, vault=True, exit=False, principal=lowerPrincipal, premium=lowerPremium, expiry=expiry)

    upperOrderId = limit_order(upperOrder)
    lowerOrderId = limit_order(lowerOrder)

    print(f'{blue}Upper Order: {blue}{stringify(upperOrder)}')
    print(f'{white}Lower Order: {white}{stringify(lowerOrder)}')

    print(f'{blue}Upper Order ID: {blue}{upperOrderId}')
    print(f'{white}Lower Order ID: {white}{lowerOrderId}')

underlying = input('what is the underlying token: ')
maturity = input('what is the market\'s maturity: ')
amount = input('how many zcTokens and nTokens do you want to use')
orderRange = input('how far from market price do you want to quote (in %): ')
expiryLength = input('how often should orders refresh: ')
PRIVATE_KEY = input('what is your private key') #or env
PROVIDER_KEY = input('what is your Infura or other provider key: ')
PUBLIC_KEY = input('what is your public key')

loop = true
while loop = true:

    simplestMarketMake(underlying, maturity, orderRange, amount, expiryLength)
    time.sleep(expiryLength)