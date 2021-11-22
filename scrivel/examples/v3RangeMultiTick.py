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

def initialRun(underlying, maturity, upperRate, lowerRate, amount, expiryLength):
    # establish the "market price"
    price = fetchPrice(underlying, math.trunc(maturity))
    price = float(price)
    # use 95% of allocated capital
    safeAmount = amount * .95 * 10**int(decimals)
    
    # annualize price to get rate
    timeDiff = maturity - time.time()
    timeModifier = (timeDiff / 31536000)
    marketRate = price / timeModifier * 100

    # determine upper / lower ranges
    upperDiff = upperRate - marketRate
    lowerDiff = marketRate - lowerRate

    # determine how spread each tick is
    upperTickDiff = upperDiff / numTicks
    lowerTickDiff = lowerDiff / numTicks

    # set initial order expiries
    expiry = float(time.time()) + expiryLength

    for i in range(numTicks):
        # determine specific tick's rate and price
        tickRate = marketRate + (upperTickDiff * (i+1))
        tickPrice = tickRate * timeModifier / 100

        exponent = numTicks-i
        # determine order size (martingale weighted)
        tickAmount = safeAmount / (2 ** exponent)

        # set specific order sizes
        principal = tickAmount
        premium = principal*tickPrice

        # create, sign, and place the order
        tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principal), premium=int(premium), expiry=int(expiry))
        signature = vendor.sign_order(tickOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")
        orderResponse = limit_order(stringify(tickOrder), signature)
        # store order and key
        orderKey = tickOrder['key'].hex()
        apiOrder = order(orderKey)
        orderKeys.append(orderKey)
        orders.append(apiOrder)

        apiOrderPrice = apiOrder['meta']['price']

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
        orderKeys.append(orderKey)

        apiOrder = order(orderKey)
        orders.append(apiOrder)
        apiOrderPrice = apiOrder['meta']['price']

        print(blue('Lower Order #'+str(i)))
        print(white(f'Lower Price: {apiOrderPrice}'))
        print(f'Lower Key: {orderKey}')
        print(' ')


def rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength):
    print('Current Time:')
    print(datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
    if initializor == 0:
        initialRun(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    else:
        # For every order in the provided range, check if it has been filled at all. If it has, place a reversed order at the same price (similar to uniswap v3)
        for i in range (0, len(orderKeys)):

            orderKey = orderKeys[i]
            returnedOrder = order(orderKey)
            newExpiry = float(time.time()) + expiryLength

            # determine if the order has been filled
            if returnedOrder['meta']['principalAvailable'] != orders[i]['meta']['principalAvailable']:

                # adjust for time difference
                timeDiff = maturity - time.time()
                price = orders[i]['meta']['price']
                timeModifier = expiryLength / timeDiff
                newPrice = price - (price * timeModifier)

                principalDiff = orders[i]['meta']['principalAvailable'] - returnedOrder['meta']['principalAvailable']
                premiumDiff = principalDiff * newPrice

                orderType = orders[i]['meta']['exit']

                # determine order type and place the new order
                if orderType == True:
                    reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                    signature = vendor.sign_order(reversedOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")     
                    orderResponse = limit_order(stringify(reversedOrder), signature)
                else:
                    reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                    signature = vendor.sign_order(reversedOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")     
                    orderResponse = limit_order(stringify(reversedOrder), signature)

                # if the order is completely filled (or 95% filled), remove it from the list
                if returnedOrder['meta']['principalAvailable'] - orders[i]['meta']['principalAvailable'] <= (orders[i]['order']['principal'] * .05):
                    orderKeys.pop(i)
                    orders.pop(i)

                # append the reversed order to the list
                orders.append(reversedOrder)
                orderKeys.append(reversedOrder['key'].hex())

                # print order info
                print(blue('New (reversed) Order:'))
                print(f'Order Key: {reversedOrder["key"].hex()}')
                print(white(f'Order Price: {reversedOrder["meta"]["price"]}'))

                # replace whatever volume has not been filled
                replacedPrincipal = returnedOrder['meta']['principalAvailable']
                recplacedPremium = replacedPrincipal * newPrice

                replacedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(replacedPrincipal), premium=int(recplacedPremium), expiry=int(newExpiry))
                signature = vendor.sign_order(reversedOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")     
                orderResponse = limit_order(stringify(reversedOrder), signature)
                
                # print order info
                print(blue('Replaced Order:'))
                print(f'Order Key: {replacedOrder["key"].hex()}')
                print(white(f'Order Price: {newPrice}'))

            # if the order has not been filled, adjust for time difference and place a new order at the same rate and principal
            else:
                # adjust for time difference
                timeDiff = maturity - time.time()
                timeModifier = expiryLength / timeDiff
                price = orders[i]['meta']['price']
                newPrice = price - (price * timeModifier)

                # determine the new premium amount
                duplicatePrincipal = orders[i]['order']['principal']
                duplicatePremium = duplicatePrincipal * newPrice

                orderExit = orders[i]['order']['exit']
                orderVault = orders[i]['order']['vault']

                duplicateOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=orderVault, exit=orderExit, principal=int(duplicatePrincipal), premium=int(duplicatePremium), expiry=int(newExpiry))
                signature = vendor.sign_order(duplicateOrder, 4, "0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA")
                orderResponse = limit_order(stringify(duplicateOrder), signature)

                # remove the order from the list
                orderKeys.pop(i)
                orders.pop(i)

                # append the duplicate order to the list
                orders.append(duplicateOrder)
                orderKeys.append(duplicateOrder['key'].hex())

                # print order info
                print(blue('New (duplicated) Order:'))
                print(f'Order Key: {reversedOrder["key"].hex()}')
                print(white(f'Order Price: {newPrice}'))


        
                
            

underlying = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa"
maturity = float(1662089767)
decimals = float(18)
amount = float(1000)
upperRate = float(20)
lowerRate = float(5)
expiryLength = float(600)
numTicks = int(3)
PUBLIC_KEY = "0x3f60008Dfd0EfC03F476D9B489D6C5B13B3eBF2C"
start()

provider = Web3.HTTPProvider("https://red-icy-surf.rinkeby.quiknode.pro/0cbdd13f2a541b199f1fb70ecc0481d9c452ae01/")
vendor = W3(provider, PUBLIC_KEY)

orderKeys = []
orders = []

initializor = 0

loop = True
while loop == True:
    rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    initializor += 1
    time.sleep(expiryLength)

stop()