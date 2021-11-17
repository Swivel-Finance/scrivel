import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..')))
from swivel.vendors import W3
from time import sleep
from sys import exit
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

def rangeMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength):

    timeDiff = maturity - time.time()
    timeModifier = (timeDiff / 31536000)

    upperPrice = upperRate * timeModifier / 100
    lowerPrice = lowerRate * timeModifier / 100 

    safeAmount = amount * .95 * 10**int(decimals)

    upperPrincipal = safeAmount
    upperPremium = upperPrincipal*upperPrice

    lowerPremium = upperPremium
    lowerPrincipal = lowerPremium/lowerPrice

    expiry = float(time.time()) + expiryLength

    upperOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(upperPrincipal), premium=int(upperPremium), expiry=int(expiry))
    lowerOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(lowerPrincipal), premium=int(lowerPremium), expiry=int(expiry))
    print(upperOrder)
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
    print(f'Upper Order Key: {upperOrderKey}')
    print(' ')
    print(f'Lower Order Price: {lowerApiOrderPrice}')
    print(f'Lower Order Key: {lowerOrderKey}')

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