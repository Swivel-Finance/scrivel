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
    underlyingCompoundRate,
)

from scrivel.helpers.colors import(
    start,
    stop,
    blue,
    white,
    green,
    red,
    cyan,
    yellow,
    magenta,
)

def fetchPrice(underlying, maturity) -> float:
    trade = last_trade(underlying, maturity)
    return trade['price']

def initialRun(underlying, maturity, upperRate, lowerRate, amount, expiryLength):
    # establish the "market price"
    price = fetchPrice(underlying, math.trunc(maturity))
    print('Current Price:')
    print(price)
    price = float(price)
    # use 95% of allocated capital
    safeAmount = amount * .95 * 10**int(decimals)
    
    # annualize price to get rate
    timeDiff = maturity - time.time()
    timeModifier = (timeDiff / 31536000)
    marketRate = price / timeModifier * 100
    print('Market Rate:')
    print(marketRate)

    # determine upper / lower ranges
    upperDiff = upperRate - marketRate
    lowerDiff = marketRate - lowerRate
    print('Upper Diff:')
    print(upperDiff)
    print('Lower Diff:')
    print(lowerDiff)
    if lowerDiff < 0 or upperDiff < 0:
        print('Error: Market rates are too high or low for range')
        exit(1)

    # determine how spread each tick is
    upperTickDiff = upperDiff / numTicks
    lowerTickDiff = lowerDiff / numTicks
    print('Upper Tick Diff:')
    print(upperTickDiff)
    print('Lower Tick Diff:')
    print(lowerTickDiff)

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
        tickOrderPrice = premium/principal

        signature = vendor.sign_order(tickOrder, 4, "0x4ccD4C002216f08218EdE1B13621faa80CecfC98")
        signature = signature

        orderResponse = limit_order(stringify(tickOrder), signature)
        # store order and key
        orderKey = tickOrder['key'].hex()
        apiOrder = order(orderKey)

        orders.append(apiOrder)

        print(red('Sell Order #'+str(i+1)))
        print(white(f'Order Price: {tickOrderPrice}'))
        print(f'Order Key: {orderKey}')
        print(f'Order Response: {orderResponse}')
        print(' ')


    for i in range(numTicks):
        tickRate = marketRate - (lowerTickDiff * (i+1))
        tickPrice = tickRate * timeModifier / 100

        exponent = numTicks-i

        lowerSafeAmount = safeAmount * price

        amount = lowerSafeAmount / (2 ** exponent)

        principal = amount / tickPrice
        premium = amount

        tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principal), premium=int(premium), expiry=int(expiry))
        tickOrderPrice = premium/principal

        signature = vendor.sign_order(tickOrder, 4, "0x4ccD4C002216f08218EdE1B13621faa80CecfC98")
        signature = signature

        orderResponse = limit_order(stringify(tickOrder), signature)
        # store order and key
        orderKey = tickOrder['key'].hex()
        apiOrder = order(orderKey)
        orders.append(apiOrder)

        print(green('Buy Order #'+str(i+1)))
        print(white(f'Order Price: {tickOrderPrice}'))
        print(f'Order Key: {orderKey}')
        print(f'Order Response: {orderResponse}')
        print(' ')


def rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength):
    print('Current Time:')
    print(datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
    print(' ')
    newOrders = []
    queuedOrderSignatures = []
    queuedOrders = []

    if initializor == 0:
        initialRun(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    else:
        # store new compound rate and establish difference
        newCompoundRate = underlyingCompoundRate(underlying, maturity)
        compoundRateDiff = (newCompoundRate - compoundRate) / compoundRate

        print('Compound Rate Variance:')
        print(str(compoundRateDiff*100)+'%')

        # For every order in the provided range, check if it has been filled at all. If it has, place a reversed order at the same price (similar to uniswap v3)
        for i in range (0, len(orders)):
            orderKey = orders[i]['order']['key']

            returnedOrder = order(orderKey)
            newExpiry = float(time.time()) + expiryLength
            principalDiff = float(orders[i]['meta']['principalAvailable']) - float(returnedOrder['meta']['principalAvailable'])

            # determine if the order has been filled, and if it is large enough to queue again
            if returnedOrder['meta']['principalAvailable'] != orders[i]['meta']['principalAvailable'] and (principalDiff >= (float(orders[i]['order']['principal']) * .05)):

                # adjust for time difference
                timeDiff = maturity - time.time()
                price = float(orders[i]['meta']['price'])
                timeModifier = expiryLength / timeDiff
                newPrice = price - (price * timeModifier)

                # adjust for changes in underlying compound rate
                compoundAdjustedImpact = newPrice * (compoundRateLean * compoundRateDiff)
                compoundAdjustedPrice = newPrice + compoundAdjustedImpact

                premiumDiff = principalDiff * compoundAdjustedPrice

                orderType = orders[i]['order']['exit']

                # determine order type and create the new order
                if orderType == True:
                    reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                    signature = vendor.sign_order(reversedOrder, 4, "0x4ccD4C002216f08218EdE1B13621faa80CecfC98")     
                    signature = signature
                else:
                    reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                    signature = vendor.sign_order(reversedOrder, 4, "0x4ccD4C002216f08218EdE1B13621faa80CecfC98")     
                    signature = signature

                # append the reversed order to the queue
                queuedOrders.append(reversedOrder)
                queuedOrderSignatures.append(signature)

                # print order info
                print(red('Queued (reversed) Order:'))
                print(f'Order Key: {reversedOrder["key"].hex()}')
                print(white(f'Order Price: {compoundAdjustedPrice}'))
                print(' ')

                # if the order is completely filled (or 95% filled), ignore it, otherwise replace the order
                if float(returnedOrder['meta']['principalAvailable']) <= (float(orders[i]['order']['principal']) * .05):
                    pass
                else:
                    # replace whatever volume has not been filled
                    replacedPrincipal = float(returnedOrder['meta']['principalAvailable'])
                    recplacedPremium = replacedPrincipal * compoundAdjustedPrice
                    
                    replacedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=orderType, principal=int(replacedPrincipal), premium=int(recplacedPremium), expiry=int(newExpiry))
                    signature = vendor.sign_order(replacedOrder, 4, "0x4ccD4C002216f08218EdE1B13621faa80CecfC98")
                    signature = signature

                    # append the replaced order to the queue
                    queuedOrders.append(replacedOrder)
                    queuedOrderSignatures.append(signature)

                    # print order info
                    print(blue('Queued (replaced) Order:'))
                    print(f'Order Key: {replacedOrder["key"].hex()}')
                    print(white(f'Order Price: {compoundAdjustedPrice}'))
                    print(' ')
                    

            # if the order has not been filled, adjust for time difference and queue a new order at the same rate and principal
            else:
                # adjust for time difference
                timeDiff = maturity - time.time()
                timeModifier = expiryLength / timeDiff
                price = float(orders[i]['meta']['price'])
                newPrice = price - (price * timeModifier)

                # adjust for changes in underlying compound rate
                compoundAdjustedImpact = newPrice * (compoundRateLean * compoundRateDiff)
                compoundAdjustedPrice = newPrice + compoundAdjustedImpact               

                # determine the new premium amount
                duplicatePrincipal = float(orders[i]['order']['principal'])
                duplicatePremium = duplicatePrincipal * compoundAdjustedPrice

                orderExit = orders[i]['order']['exit']
                orderVault = orders[i]['order']['vault']

                duplicateOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=orderVault, exit=orderExit, principal=int(duplicatePrincipal), premium=int(duplicatePremium), expiry=int(newExpiry))
                signature = vendor.sign_order(duplicateOrder, 4, "0x4ccD4C002216f08218EdE1B13621faa80CecfC98")
                signature = signature

                # append the duplicate order to the queue
                queuedOrders.append(duplicateOrder)
                queuedOrderSignatures.append(signature)

                # print order info
                print(yellow('Queued (duplicated) Order:'))
                print(f'Order Key: {duplicateOrder["key"].hex()}')
                print(white(f'Order Price: {compoundAdjustedPrice}'))
                print(' ')
        
        # print queued orders
        print(blue('Queued Orders:'))
        for i in range(len(queuedOrders)):
            orderExit = queuedOrders[i]['exit']
            orderKey = "0x..." + queuedOrders[i]['key'].hex()[-4:]
            if orderExit == True:
                orderType = "Sell nTokens"
            else:
                orderType = "Buy nTokens"
            orderPrice = round(float(queuedOrders[i]['premium']) / float(queuedOrders[i]['principal']),6)
            print(white(f'{i}. Type: {orderType}   Order Key: {orderKey}   Order Price: {orderPrice}'))

        usedOrderKeys = []
        # iterate through the orders
        for i in range (0, len(queuedOrders)):
            baseOrder = queuedOrders[i]
            baseOrderKey = queuedOrders[i]['key']
            baseOrderSignature = queuedOrderSignatures[i]

            combinedPrincipal = float(baseOrder['principal'])
            combinedPremium = float(baseOrder['premium'])
            combined = False

            # if the order has not already been combined with another order
            if baseOrderKey not in usedOrderKeys:
                # iterate through the orders again to find orders that can be combined with the current order
                for j in range (0, len(queuedOrders)):
                    # ensure not comparing to self
                    if baseOrderKey != queuedOrders[j]['key']:
                        queuedOrderPrice = queuedOrders[j]['premium'] / queuedOrders[j]['principal']
                        baseOrderPrice = baseOrder['premium'] / baseOrder['principal']
                        # if the two orders are within .005 of each other and the orderTypes are the same, combine the orders
                        if abs(queuedOrderPrice - baseOrderPrice) <= .00025 and queuedOrders[j]['exit'] == baseOrder['exit']:
                                # add the amounts to the combined order 
                                combinedPrincipal += float(queuedOrders[j]['principal'])
                                combinedPremium += float(queuedOrders[j]['premium'])
                                usedOrderKey = queuedOrders[j]['key']
                                # mark the orders that were combined as "used"
                                usedOrderKeys.append(usedOrderKey)                         

                                # print used order info
                                print(magenta(f'Combined Orders: {usedOrderKey} and {baseOrderKey}'))
                                print(white(f'Used Order: {usedOrderKey}'))

                                # set combined marker
                                combined = True
                           
                # if the order was not combined with any others, place the order
                if combined == False:
                    orderResponse = limit_order(stringify(baseOrder), baseOrderSignature)
                    apiOrder = order(baseOrderKey)  
                    orderKey = baseOrderKey.hex()
                    
                    # print order info
                    print(green('Placed Duplicate Order:'))
                    print(f'Order Key: {orderKey}')
                    print(white(f'Order Price: {apiOrder["meta"]["price"]}'))
                    print(f'Order Response: {orderResponse}')
                    print(' ')

                    # append the placed order to the list
                    newOrders.append(apiOrder)

                    # mark the order as "used"
                    usedOrderKeys.append(baseOrderKey)    
                else:
                    # create and place the combined order
                    combinedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=baseOrder['exit'], principal=int(combinedPrincipal), premium=int(combinedPremium), expiry=int(newExpiry))
                    signature = vendor.sign_order(combinedOrder, 4, "0x4ccD4C002216f08218EdE1B13621faa80CecfC98")
                    signature = signature
                    orderResponse = limit_order(stringify(combinedOrder), signature)

                    combinedOrderPrice = float(combinedOrder['premium']) / float(combinedOrder['principal'])
                    combinedOrderKey = combinedOrder['key'].hex()
                    apiOrder = order(combinedOrderKey)

                    # print order info
                    print(cyan('Placed Combined Order:'))
                    print(f'Order Key: {combinedOrderKey}')
                    print(white(f'Order Price: {combinedOrderPrice}'))
                    print(f'Order Response: {orderResponse}')
                    print(' ')

                    # mark the order as "used"
                    usedOrderKeys.append(baseOrderKey)   

                    # append the placed order to the list
                    newOrders.append(apiOrder)

        return (newOrders)


# TODO: add json storage for orders to allow user to recover position from crashes
# TODO: add exception handling and proper error messages
underlying = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa"
maturity = float(1669957199)
decimals = float(18)
amount = float(10000)
upperRate = float(18)
lowerRate = float(3)
numTicks = int(3)
expiryLength = float(300)
network = "rinkeby"
compoundRateLean = float(1)
PUBLIC_KEY = "0x3f60008Dfd0EfC03F476D9B489D6C5B13B3eBF2C"

provider = Web3.HTTPProvider("https://red-icy-surf.rinkeby.quiknode.pro/0cbdd13f2a541b199f1fb70ecc0481d9c452ae01/")
vendor = W3(provider, PUBLIC_KEY)

start()
orders = []
initializor = 0

loop = True
while loop == True:
    result = rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    if initializor != 0:
        orders = result
        print(len(orders))
    initializor += 1
    compoundRate = underlyingCompoundRate(underlying, network)
    time.sleep(expiryLength)
stop()