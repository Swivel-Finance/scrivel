import requests

# the current api-dev exposed for swivel api with a format placeholder
swivel_api_route = 'https://api-dev.swivel.exchange/v2/{}'

# update as needed...
param_keys = ('underlying', 'maturity', 'depth', 'status')

# a user may want to view non active orders
non_active_order_status = ('expired', 'cancelled', 'full', 'insolvent')

def new_params(**kwargs):
    params = {}

    for key in kwargs:
        if key in param_keys:
            params[key] = kwargs[key]

    return params

def markets(status=None):
    """Fetch all markets or only active (non-matured) from the Swivel API"""

    params = None    
    if status != None:
        params = new_params(status=status)

    resp = requests.get(swivel_api_route.format('markets'), params=params)
    return resp.json()

def last_trade(u, m):
    """Given an underlying:maturity market pair, fetch the most recent fill activity"""

    params = new_params(underlying=u, maturity=m, depth=1)
    resp = requests.get(swivel_api_route.format('fills'), params=params)
    print(resp.json())
    return resp.json()[0]

def orders(u, m, a, status=None):
    """Given a market return a list of the orders by the given address

    Description:
        Note that the status keyword may be passed to view non-active orders of the given status

    Parameters:
        u (string) market underlying
        m (int) market maturity
        a (string) public key (address) owner of the orders

        status (string) optional. one of non_active_order_status if desired

    Returns:
        List of orders belonging to the given maker
    """

    route = swivel_api_route.format('users/{}/orders'.format(a))
    params = new_params(underlying=u, maturity=m)

    if status !=None:
        params['status'] = status

    resp = requests.get(route, params)
    return resp.json()

def order(k):
    """Given a key, return the order it belongs to"""
    route = swivel_api_route.format('orders/{}'.format(k))
    resp= requests.get(route)
    return resp.json()

def limit_order(o, s):
    """Given an order and a signature, place it with the swivel api

    Returns:
        http status code, reason
    """

    resp = requests.post(swivel_api_route.format('orders'), json={'order': o, 'signature': s})
    return resp.status_code, resp.reason
