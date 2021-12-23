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

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


from scrivel.helpers.orders import new_order, stringify

from scrivel.helpers.http import (
    last_trade,
    limit_order,
    order,
    underlying_compound_rate,
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

def fetchPrice(underlying, maturity, network) -> float:
    trade = last_trade(underlying, maturity, network)
    return trade['price']

def initialRun(underlying, maturity, upperRate, lowerRate, amount, expiryLength):
    # establish the "market price"
    price = fetchPrice(underlying, math.trunc(maturity), network)

    # establish the mid-range rate
    midRate = (upperRate + lowerRate) / 2

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
    print(' ')
    print('Your Mid Rate:')
    print(midRate)
    print(' ')

    # determine upper / lower ranges
    upperDiff = upperRate - midRate
    lowerDiff = midRate - lowerRate
    print('Upper Diff:')
    print(upperDiff)
    print('Lower Diff:')
    print(lowerDiff)

    if lowerDiff < 0 or upperDiff < 0:
        print('Error: Your rates are too high or low for a real range')
        exit(1)

    # determine how spread each tick is
    upperTickDiff = upperDiff / numTicks
    lowerTickDiff = lowerDiff / numTicks

    # set initial order expiries
    expiry = float(time.time()) + expiryLength

    for i in range(numTicks):
        # determine specific tick's rate and price
        tickRate = midRate + (upperTickDiff * (i+1))
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

        signature = vendor.sign_order(tickOrder, network, swivelAddress)

        orderResponse = limit_order(stringify(tickOrder), signature, network)
        # store order and key
        orderKey = tickOrder['key'].hex()
        apiOrder = order(orderKey, network)

        orders.append(apiOrder)

        print(red('Sell Order #'+str(i+1)))
        print(white(f'Order Key: {orderKey}'))
        print(f'Order Price: {tickOrderPrice}')
        print(f'Order Rate: {tickRate}')
        principalString = str(principal/10**decimals)
        print(f'Order Amount: {principalString} nTokens')
        print(f'Order Response: {orderResponse}\n')


    for i in range(numTicks):
        tickRate = midRate - (lowerTickDiff * (i+1))
        tickPrice = tickRate * timeModifier / 100

        exponent = numTicks-i

        lowerSafeAmount = safeAmount * price

        amount = lowerSafeAmount / (2 ** exponent)

        principal = amount / tickPrice
        premium = amount

        tickOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principal), premium=int(premium), expiry=int(expiry))
        tickOrderPrice = premium/principal

        signature = vendor.sign_order(tickOrder, network, swivelAddress)

        orderResponse = limit_order(stringify(tickOrder), signature, network)
        # store order and key
        orderKey = tickOrder['key'].hex()
        apiOrder = order(orderKey, network)
        orders.append(apiOrder)

        print(green('Buy Order #'+str(i+1)))
        print(white(f'Order Key: {orderKey}'))
        print(f'Order Price: {tickOrderPrice}')
        print(f'Order Rate: {tickRate}')
        principalString = str(principal/10**decimals)
        print(f'Order Amount: {principalString} nTokens')
        print(f'Order Response: {orderResponse}\n')


def rangeMultiTickMarketMake(underlying, maturity, upperRate, lowerRate, amount, expiryLength):
    print('Current Time:')
    print(datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S\n'))
    newOrders = []
    queuedOrderSignatures = []
    queuedOrders = []

    if initializor == 0:
        initialRun(underlying, maturity, upperRate, lowerRate, amount, expiryLength)
    else:
        # store new compound rate and establish difference
        newCompoundRate = underlying_compound_rate(underlying)
        compoundRateDiff = truncate(((newCompoundRate - compoundRate) / compoundRate), 8)

        # establish the impact that time should make
        timeDiff = maturity - time.time()
        timeModifier = expiryLength / timeDiff

        print('Compound Rate Has Changed:')
        print(str(compoundRateDiff*100)+'%')

        verb = ''

        if compoundRateDiff > 0:
            verb = 'increased'
        elif compoundRateDiff < 0:
            verb = 'decreased'

        print('This change has ' + verb + 'nToken prices:')
        print(str(truncate((float(compoundRateDiff)*100*float(compoundRateLean)),6))+'%'+ ' based on your lean rate \n')

        print(str(expiryLength)+' have passed since the last quote refresh.')
        print('This has reduced nToken prices:')
        print(str(timeModifier*100)+'%\n')

        # For every order in the provided range, check if it has been filled at all. If it has, place a reversed order at the same price (similar to uniswap v3)
        for i in range (0, len(orders)):
            orderKey = orders[i]['order']['key']

            returnedOrder = order(orderKey, network)
            newExpiry = float(time.time()) + expiryLength
            principalDiff = float(orders[i]['meta']['principalAvailable']) - float(returnedOrder['meta']['principalAvailable'])

            # determine if the order has been filled, and if it is large enough to queue again
            if returnedOrder['meta']['principalAvailable'] != orders[i]['meta']['principalAvailable'] and (principalDiff >= (float(orders[i]['order']['principal']) * .05)):

                # adjust for time difference
                price = float(orders[i]['meta']['price'])
                newPrice = price - (price * timeModifier)

                # adjust for changes in underlying compound rate
                compoundAdjustedImpact = newPrice * (compoundRateLean * compoundRateDiff)
                compoundAdjustedPrice = newPrice + compoundAdjustedImpact

                premiumDiff = principalDiff * compoundAdjustedPrice

                orderType = orders[i]['order']['exit']

                print(magenta('Reversing a Filled Order...'))

                # determine order type and create the new order
                if orderType == True:
                    reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=False, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                    signature = vendor.sign_order(reversedOrder, network, swivelAddress)     
                    reversedTypeString = 'Buy'
                    typeString = 'Sell'
                    print(green('Queued ('+reversedTypeString+') Order:'))

                else:
                    reversedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=True, principal=int(principalDiff), premium=int(premiumDiff), expiry=int(newExpiry))
                    signature = vendor.sign_order(reversedOrder, network, swivelAddress)    
                    reversedTypeString = 'Sell' 
                    typeString = 'Buy'
                    print(red('Queued ('+reversedTypeString+') Order:'))

                # append the reversed order to the queue
                queuedOrders.append(reversedOrder)
                queuedOrderSignatures.append(signature)

                # print order info
                print(f'Order Key: {reversedOrder["key"].hex()}')
                print(white(f'Order Price: {compoundAdjustedPrice}'))
                principalString = str(principalDiff/10**decimals)
                print(f'Order Amount: {principalString} nTokens')

                # if the order is completely filled (or 95% filled), ignore it, otherwise replace the remaining order volume
                if float(returnedOrder['meta']['principalAvailable']) <= (float(orders[i]['order']['principal']) * .05):
                    pass
                else:
                    # replace whatever volume has not been filled
                    replacedPrincipal = float(returnedOrder['meta']['principalAvailable'])
                    recplacedPremium = replacedPrincipal * compoundAdjustedPrice
                    
                    replacedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=orderType, principal=int(replacedPrincipal), premium=int(recplacedPremium), expiry=int(newExpiry))
                    signature = vendor.sign_order(replacedOrder, network, swivelAddress)

                    # append the replaced order to the queue
                    queuedOrders.append(replacedOrder)
                    queuedOrderSignatures.append(signature)

                    # print order info
                    print(cyan('Replacing Remaining order volume...'))
                    if orderType == True:
                        print(red('Queued (' + typeString + ') Order:'))
                    else:
                        print(green('Queued (' + typeString + ') Order:'))

                    print(f'Order Key: {replacedOrder["key"].hex()}')
                    print(white(f'Order Price: {compoundAdjustedPrice}\n'))
                    principalString = str(replacedPrincipal/10**decimals)
                    print(f'Order Amount: {principalString} nTokens')
                    

            # if the order has not been filled, adjust for time difference and queue a new order at the same rate and principal
            else:
                # adjust for time difference
                price = float(orders[i]['meta']['price'])
                newPrice = price - (price * timeModifier)

                # adjust for changes in underlying compound rate
                compoundAdjustedImpact = newPrice * (compoundRateLean * compoundRateDiff)
                compoundAdjustedPrice = newPrice + compoundAdjustedImpact               

                # determine the new premium amount
                duplicatePrincipal = float(orders[i]['order']['principal'])
                duplicatePremium = duplicatePrincipal * compoundAdjustedPrice

                orderExit = orders[i]['order']['exit']

                # establish order typestring
                if orderExit == True:
                    typeString = "Sell"
                else:
                    typeString = "Buy"
                duplicateOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=orderExit, principal=int(duplicatePrincipal), premium=int(duplicatePremium), expiry=int(newExpiry))
                signature = vendor.sign_order(duplicateOrder, network, swivelAddress)

                # append the duplicate order to the queue
                queuedOrders.append(duplicateOrder)
                queuedOrderSignatures.append(signature)

                # print order info
                print(yellow('Queued duplicate (' + typeString + ') Order:'))
                print(f'Order Key: {duplicateOrder["key"].hex()}')
                print(white(f'Order Price: {compoundAdjustedPrice}\n'))
                principalString = str(duplicatePrincipal/10**decimals)
                print(f'Order Amount: {principalString} nTokens')
        
        # print queued orders
        print(magenta('Queued Orders:'))
        for i in range(len(queuedOrders)):
            orderExit = queuedOrders[i]['exit']
            orderKey = "0x..." + queuedOrders[i]['key'].hex()[-4:]
            if orderExit == True:
                orderType = "Sell nTokens"
            else:
                orderType = "Buy nTokens"
            orderPrice = round(float(queuedOrders[i]['premium']) / float(queuedOrders[i]['principal']),6)
            orderNum = i+1
            print(white(f'{orderNum}. Type: {orderType}   Order Key: {orderKey}   Order Price: {orderPrice}'))
        print('')

        usedOrderKeys = []
        # iterate through the orders
        for i in range (0, len(queuedOrders)):
            baseOrder = queuedOrders[i]
            baseOrderKey = queuedOrders[i]['key']
            baseOrderKey = baseOrderKey.hex()
            baseOrderSignature = queuedOrderSignatures[i]

            combinedPrincipal = float(baseOrder['principal'])
            combinedPremium = float(baseOrder['premium'])
            combined = False

            # if the order has not already been combined with another order
            if baseOrderKey not in usedOrderKeys:
                # iterate through the orders again to find orders that can be combined with the current order
                for j in range (0, len(queuedOrders)):

                    queuedOrder = queuedOrders[j]
                    queuedOrderKey = queuedOrders[j]['key'].hex()
                    # ensure not comparing to self
                    if baseOrderKey != queuedOrderKey:
                        queuedOrderPrice = queuedOrder['premium'] / queuedOrder['principal']
                        baseOrderPrice = baseOrder['premium'] / baseOrder['principal']
                        # if the two orders are within .005 of each other and the orderTypes are the same, combine the orders
                        if abs(queuedOrderPrice - baseOrderPrice) <= .00025 and queuedOrder['exit'] == baseOrder['exit']:
                                # add the amounts to the combined order 
                                combinedPrincipal += float(queuedOrder['principal'])
                                combinedPremium += float(queuedOrder['premium'])
                                usedOrderKey = queuedOrderKey
                                # mark the orders that were combined as "used"
                                usedOrderKeys.append(usedOrderKey)

                                printedUsedOrderKey = "0x..." + usedOrderKey[-4:]                     
                                printedBaseOrderKey = "0x..." + baseOrderKey[-4:]  

                                # print used order info
                                print(magenta('Combined Orders with a price of ' + str(truncate(queuedOrderPrice,4)) + f': {printedUsedOrderKey} and {printedBaseOrderKey}'))
                                print(white(f'Used Order: {usedOrderKey}\n'))

                                # set combined marker
                                combined = True
                           
                # if the order was not combined with any others, place the order
                if combined == False:
                    orderResponse = limit_order(stringify(baseOrder), baseOrderSignature, network)
                    orderKey = baseOrderKey
                    apiOrder = order(orderKey, network)  

                    # establish order typestring + print order type
                    orderExit = apiOrder['order']['exit']
                    if orderExit == True:
                        typeString = "Sell"
                        print(red('Placed ' + typeString + ' Order:'))
                    else:
                        typeString = "Buy"
                        print(green('Placed ' + typeString + ' Order:'))

                    # print order info
                    print(f'Order Key: {orderKey}')
                    print(white(f'Order Price: {apiOrder["meta"]["price"]}'))
                    principalString = str(float(apiOrder["meta"]["principalAvailable"])/10**decimals)
                    print(f'Order Amount: {principalString} nTokens')
                    print(f'Order Response: {orderResponse}\n')

                    # append the placed order to the list
                    newOrders.append(apiOrder)

                    # mark the order as "used"
                    usedOrderKeys.append(orderKey)    
                else:
                    # create and place the combined order
                    combinedOrder = new_order(PUBLIC_KEY, underlying=underlying, maturity=int(maturity), vault=True, exit=baseOrder['exit'], principal=int(combinedPrincipal), premium=int(combinedPremium), expiry=int(newExpiry))
                    signature = vendor.sign_order(combinedOrder, network, swivelAddress)
                    
                    orderResponse = limit_order(stringify(combinedOrder), signature, network)

                    combinedOrderPrice = float(combinedPremium) / float(combinedPrincipal)
                    combinedOrderKey = combinedOrder['key'].hex()
                    apiOrder = order(combinedOrderKey, network)

                    # establish order typestring
                    orderExit = apiOrder['order']['exit']
                    if orderExit == True:
                        typeString = "Sell"
                    else:
                        typeString = "Buy"


                    # print order info
                    print(cyan('Placed Combined ' + typeString + ' Order:'))
                    print(f'Order Key: {combinedOrderKey}')
                    print(white(f'Order Price: {combinedOrderPrice}'))
                    principalString = str(combinedPrincipal/10**decimals)
                    print(f'Order Amount: {principalString} nTokens')
                    print(f'Order Response: {orderResponse}\n')

                    # mark the order as "used"
                    usedOrderKeys.append(baseOrderKey)   

                    # append the placed order to the list
                    newOrders.append(apiOrder)

        return (newOrders)


# TODO: add json storage for orders to allow user to recover position from crashes
# TODO: add exception handling and proper error messages

# Market
underlying = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa" # The underlying token address
maturity = float(1669957199) # The Swivel market maturity in unix
decimals = float(18) # The decimals of the underlying token
networkString = "rinkeby"

# Position
amount = float(10000) # The amount of nTokens to use market-making
upperRate = float(9) # The highest rate at which to quote 
lowerRate = float(6.75) # The lowest rate at which to quote 
numTicks = int(3) # The number of liquidity ticks to split your amount into
expiryLength = float(20) # How often orders should be refreshed (in seconds) 
compoundRateLean = float(1) # How much your quote should change when Compound’s rate varies (e.g. 1 = 1:1 change in price) 

PUBLIC_KEY = "0x3f60008Dfd0EfC03F476D9B489D6C5B13B3eBF2C"
provider = Web3.HTTPProvider("<YOUR_PROVIDER_KEY>")
vendor = W3(provider, PUBLIC_KEY)

if networkString == "mainnet":
    network = 1
    swivelAddress = "0x3b983B701406010866bD68331aAed374fb9f50C9"
elif networkString == "rinkeby":
    network = 4
    swivelAddress = "0x4ccD4C002216f08218EdE1B13621faa80CecfC98"
elif networkString == "kovan":
    network = 42
    swivelAddress = "0x301292f76885b5a20c7dbd0e06F093E9D4e5fA3F"
else:
    print("Invalid network")
    exit(1)
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
    compoundRate = underlying_compound_rate(underlying)
    time.sleep(expiryLength)
stop()