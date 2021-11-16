import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))
from swivel.vendors import W3
from time import sleep
from sys import exit
import time
import datetime
import math

from web3 import Web3

from scrivel.helpers.orders import new_order, stringify, parse

from scrivel.helpers.http import (
    last_trade,
    limit_order,
)

from scrivel.helpers.colors import(
    blue,
    white,
)

def fetchPrice(underlying, maturity) -> float:
    trade = last_trade(underlying, maturity)
    return trade['price']

def simplestMarketMake(underlying, maturity, range, amount, expiryLength):

    price = fetchPrice(underlying, math.trunc(maturity))
    price = float(price)
    upperBound = price + (price*(range/100))
    lowerBound = price - (price*(range/100))

    safeAmount = amount * .95 * 10**int(decimals)
    
    splitAmount = safeAmount / 2

    upperPrincipal = splitAmount
    upperPremium = splitAmount*upperBound

    lowerPrincipal = splitAmount/lowerBound
    lowerPremium = splitAmount

    expiry = float(time.time()) + expiryLength

    upperOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(upperPrincipal), premium=int(upperPremium), expiry=int(expiry))

    lowerOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(lowerPrincipal), premium=int(lowerPremium), expiry=int(expiry))
    
    print(blue("\nUpper Order: "))
    print(stringify(upperOrder))

    provider = Web3.HTTPProvider("https://red-icy-surf.rinkeby.quiknode.pro/0cbdd13f2a541b199f1fb70ecc0481d9c452ae01/")

    vendor = W3(provider, PUBLIC_KEY)

    upperOrderSignature = vendor.sign_order(upperOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")

    lowerOrderSignature = vendor.sign_order(lowerOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")

    upperOrderId = limit_order(upperOrder, upperOrderSignature)
    lowerOrderId = limit_order(lowerOrder, lowerOrderSignature)

    print(f'{blue}Upper Order: {blue}{stringify(upperOrder)}')
    print(f'{white}Lower Order: {white}{stringify(lowerOrder)}')

    print(f'{blue}Upper Order ID: {blue}{upperOrderId}')
    print(f'{white}Lower Order ID: {white}{lowerOrderId}')

underlying = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa"
maturity = float(1662089767)
decimals = float(18)
amount = float(1000)
orderRange = float(5)
expiryLength = float(10000)
PUBLIC_KEY = "0x7111F9Aeb2C1b9344EC274780dc9e3806bdc60Ef"

loop = True
while loop == True:

    simplestMarketMake(underlying, maturity, orderRange, amount, expiryLength)
    time.sleep(expiryLength)