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

from scrivel.helpers.orders import new_order, stringify

from scrivel.helpers.http import (
    last_trade,
    limit_order,
    order,
)

from scrivel.helpers.colors import(
    start,
    stop,
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

    lowerPremium = upperPremium
    lowerPrincipal = lowerPremium/lowerBound

    expiry = float(time.time()) + expiryLength

    upperOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(upperPrincipal), premium=int(upperPremium), expiry=int(expiry))

    lowerOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(lowerPrincipal), premium=int(lowerPremium), expiry=int(expiry))

    provider = Web3.HTTPProvider("https://red-icy-surf.rinkeby.quiknode.pro/0cbdd13f2a541b199f1fb70ecc0481d9c452ae01/")

    vendor = W3(provider, PUBLIC_KEY)

    upperOrderSignature = vendor.sign_order(upperOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")

    lowerOrderSignature = vendor.sign_order(lowerOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")

    upperOrderResponse = limit_order(stringify(upperOrder), upperOrderSignature)
    lowerOrderResponse = limit_order(stringify(lowerOrder), lowerOrderSignature)

    upperOrderKey = upperOrder['key'].hex()
    lowerOrderKey = lowerOrder['key'].hex()

    upperApiOrderPrice = order(upperOrderKey)['meta']['price']
    lowerApiOrderPrice = order(lowerOrderKey)['meta']['price']

    print(blue('Successfully replaced positions.'))
    print(white(' '))
    print('Current Time:')
    print(datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
    print('Order Expiry:')
    print(datetime.datetime.utcfromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S'))
    print(' ')
    print(f'Upper Order Price: {upperApiOrderPrice}')
    print(f'Upper Order Key: {lowerOrderKey}')
    print(' ')
    print(f'Lower Order Price: {lowerApiOrderPrice}')
    print(f'Lower Order Key: {upperOrderKey}')
    

underlying = input('What is the underlying token address: ') #"0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa"
maturity = float(input('What is the market maturity: ')) #float(1662089767)
decimals = float(input('How many decimals does the token have: ')) #float(18)
amount = float(input('How many nTokens do you want to use as inventory (must have equivalent underlying inventory): ')) #float(1000)
orderRange = float(input('How far from market price do you want to quote: ')) #float(5)
expiryLength = float(input('How often do you want to update your orders: ')) #float(600)
PUBLIC_KEY = input('What is your public key:') #"0x7111F9Aeb2C1b9344EC274780dc9e3806bdc60Ef"
start()
loop = True
while loop == True:

    simplestMarketMake(underlying, maturity, orderRange, amount, expiryLength)
    time.sleep(expiryLength)
stop()