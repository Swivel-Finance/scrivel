import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))
from swivel.vendors import W3
from time import sleep
from sys import exit
import math
import time
import datetime
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


def rangeMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength):

    price = fetchPrice(underlying, math.trunc(maturity))
    price = float(price)

    safeAmount = amount * .95 * 10**int(decimals)

    timeDiff = maturity - time.time()
    timeModifier = (timeDiff / 31536000)

    marketRate = price / timeModifier * 100

    upperDiff = upperRate - marketRate
    print('upper diff')
    print(upperDiff)
    lowerDiff = marketRate - lowerRate
    upperTickDiff = upperDiff / numTicks
    print('upper tick diff')
    print(upperTickDiff)

    lowerTickDiff = lowerDiff / numTicks

    expiry = float(time.time()) + expiryLength

    provider = Web3.HTTPProvider("https://red-icy-surf.rinkeby.quiknode.pro/0cbdd13f2a541b199f1fb70ecc0481d9c452ae01/")
    vendor = W3(provider, PUBLIC_KEY)

    print('Current Time:')
    print(datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))

    for i in range(numTicks):
        tickRate = marketRate + (upperTickDiff * (i+1))
        tickPrice = tickRate * timeModifier / 100

        exponent = numTicks-i

        tickAmount = safeAmount / (2 ** exponent)

        principal = tickAmount
        premium = principal*tickPrice

        tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principal), premium=int(premium), expiry=int(expiry))
        signature = vendor.sign_order(tickOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")

        orderResponse = limit_order(stringify(tickOrder), signature)

        print(orderResponse)

        orderKey = tickOrder['key'].hex()

        apiOrderPrice = order(orderKey)['meta']['price']

        print(apiOrderPrice)

        print('Upper Order #'+str(i))
        print(f'Order Price: {apiOrderPrice}')
        print(f'Order Key: {orderKey}')
        print(' ')


    for i in range(numTicks):
        tickRate = marketRate - (lowerTickDiff * (i+1))
        tickPrice = tickRate * timeModifier / 100

        exponent = numTicks-i

        amount = safeAmount / (2 ** exponent)

        premium = tickAmount
        principal = premium/tickPrice

        tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principal), premium=int(premium), expiry=int(expiry))

        signature = vendor.sign_order(tickOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")

        orderResponse = limit_order(stringify(tickOrder), signature)

        orderKey = tickOrder['key'].hex()

        apiOrderPrice = order(orderKey)['meta']['price']

        print('Lower Order #'+str(i))
        print(f'Lower Price: {apiOrderPrice}')
        print(f'Lower Key: {orderKey}')
        print(' ')

underlying = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa"
maturity = float(1662089767)
decimals = float(18)
amount = float(1000)
expiryLength = float(600)
upperRate = float(30)
lowerRate = float(17.5)
numTicks = int(3)
PUBLIC_KEY = "0x3f60008Dfd0EfC03F476D9B489D6C5B13B3eBF2C"

start()

loop = True
while loop == True:

    rangeMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    time.sleep(expiryLength)

stop()