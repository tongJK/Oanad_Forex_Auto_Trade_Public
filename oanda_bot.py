import oandapyV20

import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.transactions as transactions


from math import pow
from oandapyV20.exceptions import V20Error


def use_our_token():

    account_id = ''
    access_token = ''

    client = oandapyV20.API(access_token=access_token)

    return account_id, client


def generate_user_token(acc_token):
    access_token = acc_token
    client = oandapyV20.API(access_token=access_token)

    return client


def calculate_stop_lose_or_take_profit_point(price, low_pips, high_pips, mode):
    """
    :param price: current price or market if touch price
    :param low_pips: how many pips that user can take in stop loss price or take profit price
    :param high_pips: how many pips that user can take in stop loss price or take profit price

    :param mode: 0  is  buy order [stop loss < price]
                 1  is  sell order  [stop loss > price]


    :return: mode: 0  is  low_price, high_price [low_price = stop loss price, high_price = take profit price] # buy
                   1  is  high_price, low_price [high_price = stop loss price, low_price = take profit price] # sell

    """
    low_pips *= 10
    high_pips *= 10

    b = f"{'0' * int(len(price.split('.')[0]))}.{'0' * int(len(price.split('.')[1]) - 1)}1"

    d = float(b) * low_pips
    e = float(b) * high_pips

    if mode == 0:  # buy order

        low_price = f"{float(price) - d}{'0' * int(len(price) - len(str(float(price) - d)))}"[:len(price)]

        high_price = f"{float(price) + e}{'0' * int(len(price) - len(str(float(price) - e)))}"[:len(price)]

        return low_price, high_price

    else:  # sell order

        low_price = f"{float(price) - e}{'0' * int(len(price) - len(str(float(price) - e)))}"[:len(price)]

        high_price = f"{float(price) + d}{'0' * int(len(price) - len(str(float(price) - d)))}"[:len(price)]

        return high_price, low_price


def calculate_take_profit_state(st_1, st_2, mode):

    st_2 *= 10

    b = f"{'0' * int(len(st_1.split('.')[0]))}.{'0' * int(len(st_1.split('.')[1]) - 1)}1"

    d = float(b) * st_2

    if mode == 1:
        state_2 = f"{float(st_1) - d}{'0' * int(len(st_1) - len(str(float(st_1) - d)))}"

    else:
        state_2 = f"{float(st_1) + d}{'0' * int(len(st_1) - len(str(float(st_1) - d)))}"

    return state_2[:len(st_1)]


# ---------- Order with Take Profit and Stop Loss ---------------------------------------------------------------------

def sell_by_limit(account_id, account_token, instrument, unit, sell_price, stl_price, tf_price, debug=False):

    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": sell_price,
                "takeProfitOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": tf_price
                    },
                "stopLossOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": stl_price
                    },
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"-{unit}",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "77777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        return True, r.response['orderFillTransaction']['tradeOpened']['tradeID']

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")

        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


def sell_if_touched(account_id, account_token, instrument, unit, sell_price, stl_price, tf_price, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": sell_price,
                "takeProfitOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": tf_price
                    },
                "stopLossOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": stl_price
                    },
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"-{unit}",
                "type": "MARKET_IF_TOUCHED",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "777777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        return True, r.response['orderFillTransaction']['tradeOpened']['tradeID']

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")

        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


def buy_by_limit(account_id, account_token, instrument, unit, buy_price, stl_price, tf_price, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": buy_price,
                "takeProfitOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": tf_price
                    },
                "stopLossOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": stl_price
                    },
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"{unit}",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "77777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        trade_id = r.response['orderFillTransaction']['tradeOpened']['tradeID']

        return True, trade_id

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")

        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


def buy_if_touch(account_id, account_token, instrument, unit, buy_price, stl_price, tf_price, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": buy_price,
                "takeProfitOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": tf_price
                    },
                "stopLossOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": stl_price
                    },
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"{unit}",
                "type": "MARKET_IF_TOUCHED",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "77777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        return True, r.response['orderFillTransaction']['tradeOpened']['tradeID']

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")
        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


# ---------- Order WHITOUT Take Profit and Stop Loss ------------------------------------------------------------------

def sell_without_tp(account_id, account_token, instrument, unit, sell_price, stl_price, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": sell_price,
                "stopLossOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": stl_price
                    },
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"-{unit}",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "77777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        return True, r.response['orderFillTransaction']['tradeOpened']['tradeID']

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")

        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


def buy_without_tp(account_id, account_token, instrument, unit, buy_price, stl_price, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": buy_price,
                "stopLossOnFill":
                    {
                        "timeInForce": "GTC",
                        "price": stl_price
                    },
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"{unit}",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "77777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        trade_id = r.response['orderFillTransaction']['tradeOpened']['tradeID']

        return True, trade_id

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")

        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


# ---------- Order WHITOUT Take Profit and Stop Loss ------------------------------------------------------------------

def sell_without_tp_sl(account_id, account_token, instrument, unit, sell_price, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": sell_price,
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"-{unit}",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "77777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        return True, r.response['orderFillTransaction']['tradeOpened']['tradeID']

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")

        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


def buy_without_tp_sl(account_id, account_token, instrument, unit, buy_price, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    data = {
        "order":
            {
                "price": buy_price,
                "timeInForce": "GTC",
                "instrument": instrument,
                "units": f"{unit}",
                "type": "LIMIT",
                "positionFill": "DEFAULT",
                "clientExtensions":
                    {
                        "id": "77777",
                        "tag": "66666",
                        "comment": "NUEVE_AUTO_BOT"
                    }
            }
    }

    try:

        r = orders.OrderCreate(account_id, data=data)

        client.request(r)
        print(r.response)

        trade_id = r.response['orderFillTransaction']['tradeOpened']['tradeID']

        return True, trade_id

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        # print(ex.msg.split('"errorMessage":')[1].split(',')[1].split('}')[0])
        print(f"Error : {error_msg}")

        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


# ---------------------------------------------------------------------------------------------------------------------


def call_order_list(account_id, account_token, instrument, debug=False):
    trade_list = []

    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    params = {"instrument": instrument}

    try:
        r = orders.OrderList(accountID=account_id, params=params)

        client.request(r)
        # print(r.response)
        # print('\n')

        for num, res in enumerate(r.response['orders']):
            # print(f"order {instrument!r} no.{num} has trade ID : {res['tradeID']}")

            trade_list.append(res['tradeID'])

        return trade_list

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0]
        print(f"Error : {error_msg}")

        return error_msg


def close_order(account_id, account_token, trade_id, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    try:
        r = trades.TradeClose(accountID=account_id, tradeID=f'{trade_id}')

        client.request(r)
        print(r.response)

        return True, 'Your Order has been Closed'

    except V20Error as ex:

        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0]
        print(f"Error : {error_msg}")

        return False, error_msg


def get_trade_details(account_id, account_token, trade_id, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    try:
        r = trades.TradeDetails(account_id, tradeID=f'{trade_id}')

        client.request(r)
        # print(r.response)

        trade_details = r.response["trade"]

        print('\n')

        trade_detail = f"order ID {trade_details['id']!r} | Instrument : {trade_details['instrument']!r} | "\
            f"Price : {trade_details['price']!r} | Unit : {trade_details['initialUnits']!r} | "\
            f"Profit/Loss = {trade_details['unrealizedPL']}"

        # print(trade_detail)

        return trade_detail

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0]
        print(f"Error : {error_msg}")
        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


def get_trade_profit(account_id, account_token, trade_id, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    try:
        r = trades.TradeDetails(account_id, tradeID=f'{trade_id}')

        client.request(r)
        # print(r.response)

        trade_profit = float(r.response["trade"]['unrealizedPL'])
        # print(f"\ntrade_profit = {trade_profit}")

        return trade_profit

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0]
        print(f"Error : {error_msg}")
        return False, error_msg

    except Exception as ex:
        template = "Exception type {0}. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(f"Error : {message}")
        return False, message


def ask_prices(account_id, account_token, instrument_s, debug=False, print_price=True):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    # params = {"instruments": "EUR_USD,EUR_JPY"}
    params = {"instruments": instrument_s}

    try:
        r = pricing.PricingInfo(accountID=account_id, params=params)

        client.request(r)
        # print(r.response)

        prices = r.response
        # print(prices)

        sell_price = prices["prices"][0]["bids"][0]["price"]
        buy_price = prices["prices"][0]["asks"][0]["price"]

        if print_price:
            print(f"sell_price = {sell_price}")
            print(f"buy_price = {buy_price}")

        return sell_price, buy_price

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0]
        print(f"Error : {error_msg}")

        return False, error_msg


def get_user_account_details(account_id, account_token, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    try:

        r = accounts.AccountDetails(account_id)

        client.request(r)
        # print(r.response)

        user_balance = r.response['account']['balance']
        print(f'user balance = {user_balance}')

        return r.response

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0]
        print(f"Error : {error_msg}")

        return error_msg


def get_transaction_details(account_id, account_token, trade_id, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    try:

        r = transactions.TransactionDetails(account_id, trade_id)

        client.request(r)
        # print(r.response)

        transaction_reason = r.response['transaction']['reason']
        profit_loss = r.response['transaction']['pl']

        print(f'user order closed by : {transaction_reason}, Profit/Loss = {profit_loss}')

        """
        ON_FILL
        MARKET_ORDER_TRADE_CLOSE
        TAKE_PROFIT_ORDER
        STOP_LOSS_ORDER
        CLIENT_ORDER
        CLIENT_REQUEST
        """

        return transaction_reason, profit_loss

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0]
        print(f"Error : {error_msg}")

        return False, error_msg


def calculate_maximum_unit(account_id, account_token, unit, debug=False):
    if debug:
        account_id, client = use_our_token()

    else:
        client = account_token

    try:
        r1 = accounts.AccountSummary(account_id)
        client.request(r1)

        base_currency = unit[:3]
        home_currency = r1.response['account']['currency']

        base_home = f"{base_currency}_{home_currency}"

        margin_ratio = float(r1.response['account']['marginRate'][:4])
        margin_avaliable = float(r1.response['account']['marginAvailable'])

        if base_currency != 'USD':
            r2 = pricing.PricingInfo(accountID=account_id, params={"instruments": base_home})
            client.request(r2)

            current_price = float(r2.response['prices'][0]['asks'][0]['price'])

        else:
            current_price = 1

        maximum_unit = (margin_avaliable * pow(margin_ratio, -1)) / current_price

        return int(maximum_unit)

    except V20Error as ex:
        error_msg = ex.msg.split('"errorMessage":')[1].split(',')[0].replace('}', '')
        print(f"Error : {error_msg}")

        return error_msg
