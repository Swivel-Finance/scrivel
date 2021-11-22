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


def rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength):

    price = fetchPrice(underlying, math.trunc(maturity))
    price = float(price)

    safeAmount = amount * .95 * 10**int(decimals)

    timeDiff = maturity - time.time()
    timeModifier = (timeDiff / 31536000)

    marketRate = price / timeModifier * 100

    upperDiff = upperRate - marketRate
    lowerDiff = marketRate - lowerRate

    upperTickDiff = upperDiff / numTicks
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

        orderKey = tickOrder['key'].hex()

        apiOrderPrice = order(orderKey)['meta']['price']

        print(blue('Upper Order #'+str(i)))
        print(white(f'Order Price: {apiOrderPrice}'))
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

        print(blue('Lower Order #'+str(i)))
        print(white(f'Lower Price: {apiOrderPrice}'))
        print(f'Lower Key: {orderKey}')
        print(' ')

underlying = input('What is the underlying token address: ') #"0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa"
maturity = float(input('What is the market maturity: ')) #float(1662089767)
decimals = float(input('How many decimals does the token have: ')) #float(18)
amount = float(input('How many nTokens do you want to use as inventory (must have equivalent underlying inventory): ')) #float(1000)
upperRate = float(input('What is the max rate you want to predict: ')) #float(20)
lowerRate = float(input('What is the minimum rate you want to predict: ')) #float(5)
numTicks = int(input('How many ticks do you want to make: ')) #int(3)
expiryLength = float(input('How often do you want to update your orders: ')) #float(600)
PUBLIC_KEY = input('What is your public key: ') #"0x7111F9Aeb2C1b9344EC274780dc9e3806bdc60Ef"
start()

loop = True
while loop == True:

    rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    time.sleep(expiryLength)

stop()