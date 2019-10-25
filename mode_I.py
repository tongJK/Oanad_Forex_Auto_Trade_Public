
"""
 Last Update : 16/08/2019
 Note : Test First Order and check

"""

# [✔]   เช็คจุด get predict ว่า instrument ตรงกับ 10 คู่ของ predict ที่มีมั้ย
# [✔]   เอา condition ของ state 3 ไปใช้กับ condition state 7
# [x]   ต้องเพิ่ม state 9 เพื่อใช้เช็ค second order มั้ย
# [✔]   put Activities_Log and check again
# [✔]   put Trade_History in db
# [✔]   put STATUS_LOG in db
# [✔]   put EXIT_LOG in db
# [✔]   put check loss 3 orders continuously function


# [✔]   loss orders in continuously function
# [ ]   increase/decreased candle stick function


# ---------------------------------------------------------------------------------------------------------------------

import base64
from time import sleep, strftime


from oanda_bot import *
from activities_log import log_creator
from database_connection import get_forex_predict, connect_2_database, update_trade_history, _update_bot_status, \
    check_switch, close_bot


def forex_mi_main(user_id, slot):

    api_key = None
    secret_key = None

    while True:

        # -------------------------------------------------------------------------------------------------------------
        # -------------------- STATE I : Get User Config from Database ------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        print('\n', '-'*30, 'STATE I', '-'*30, '\n')

        # Get value and setting config from user

        _update_bot_status(user_id, slot, 'Bot Starting')

        try:

            my_db = connect_2_database()
            cur = my_db.cursor()

            sql_select = "SELECT user_id, slot, currency, trade_limit, side, cut_loss_switch, take_profit, " \
                         "mode2_take_profit_2, mode2_take_profit_3, stop_loss" \
                         " FROM FOREX_setting WHERE user_id = '{}'".format(user_id)

            cur.execute(sql_select)
            query_result = cur.fetchone()

            user_id = query_result[0]
            slot = query_result[1]

            symbol = query_result[2]
            unit_1 = query_result[3]

            spare_first_order_type = query_result[4]
            # stop_loss_switch = query_result[5]

            pips_tp_1 = query_result[6]
            # pips_tp_2 = query_result[7]
            # pips_tp_3 = query_result[8]
            pips_sl_1 = query_result[9]

            # print(user_id, slot, symbol, unit_1, spare_first_order_type, pips_tp_1, pips_sl_1)
            # continue

        except Exception as e:

            print(f"Database Connection Part_1 Fail by {e}")
            # log_creator(user_id, slot, f"Database Connection Part_1 Fail by {e}", 0, 1)
            sleep(5)
            continue

        # Create Log File

        log_msg = f"Mode I\nInstrument : {symbol!r} | Order Option : {spare_first_order_type}\n" \
            f"Order Detail : [Unit : {unit_1} | SLP : {pips_sl_1} | TPP_1 : {pips_tp_1}"

        print(log_msg)
        log_creator(user_id, slot, log_msg, header=True)

        _update_bot_status(user_id, slot, 'Get Bot Setting From User')

        # Check Unit and Pips are Interger
        try:
            unit_1 = int(unit_1)

            pips_sl_1 = int(pips_sl_1)
            pips_tp_1 = int(pips_tp_1)

        except ValueError:
            print("Unit and Pips must be integer")
            log_creator(user_id, slot, "Unit and Pips must be integer", 0, 1)

            _update_bot_status(user_id, slot, 'Unit and Pips must be integer', mode=0)
            # sent_mail(user_id, slot)
            exit(0)

        # Get user's account id and token key
        try:
            sql_select = "SELECT api_key, secret_key, status FROM data_bot WHERE user_id = '{}' "\
                         "AND exchanges_code = 1".format(user_id)

            cur.execute(sql_select)
            query_result = cur.fetchone()

            log_creator(user_id, slot, f"Get user account, token key and decoded", state_write=1)

        except Exception as e:

            print(f"Database Connection Part_2 Fail by {e}")
            log_creator(user_id, slot, f"Database Connection Part_2 Fail by {e}", 0, 1)
            sleep(5)
            continue

        finally:
            if cur:
                cur.close()
            if my_db:
                my_db.close()

        # Check API Switch
        if query_result[2] == 'on':  # API ON
            api_key = bytes.fromhex(query_result[0])
            api_key = base64.b64decode(api_key).decode("utf-8")
            secret_key = bytes.fromhex(query_result[1])
            secret_key = base64.b64decode(secret_key).decode("utf-8")

            # api_key = query_result[0]
            # secret_key = query_result[1]

            print("Decode AccountID & Token : SUCCESSFULLY")
            log_creator(user_id, slot, "Decode Account ID & Token : SUCCESSFULLY")

            _update_bot_status(user_id, slot, 'Connect to API Successfully')

        else:  # API OFF
            print("Decode Account ID & Token : FAIL [Bot_Status is OFF]")
            log_creator(user_id, slot, "Decode AccountID & Token : FAIL [Bot_Status is OFF]", 0)

            _update_bot_status(user_id, slot, 'Decode AccountID & Token : FAIL [Bot_Status is OFF]', mode=0)
            # sent_mail(user_id, slot)
            exit(0)

        # -------------------------------------------------------------------------------------------------------------
        # -------------------- STATE II : Generate API Client from User id and token ----------------------------------
        # -------------------------------------------------------------------------------------------------------------

        print('\n', '-' * 30, 'STATE II', '-' * 30, '\n')

        if not api_key or not secret_key:
            print('api_key or secret_key is null')
            log_creator(user_id, slot, "api_key or secret_key is null", 0, 2)

            _update_bot_status(user_id, slot, 'api_key or secret_key is null', mode=0)
            # sent_mail(user_id, slot)
            exit(0)

        try:  # Connection PASS

            _update_bot_status(user_id, slot, 'Generate Token')

            client = generate_user_token(secret_key)

            print("Generate client for user SUCCESSFULLY")
            log_creator(user_id, slot, "Generate client for user SUCCESSFULLY", state_write=2)

        except Exception as e:  # Connection FAIL
            print(f"Generate client for user FAIL : [{e}]")
            log_creator(user_id, slot, f"Generate client for user FAIL : [{e}]", 0, 2)

            _update_bot_status(user_id, slot, 'Fail in Generate Token / Re-Generate', 0)

            sleep(5)
            continue

        # -------------------------------------------------------------------------------------------------------------
        # -------------------- STATE III : Check Conditions for First Order from User's config ------------------------
        # -------------------------------------------------------------------------------------------------------------

        print('\n', '-' * 30, 'STATE III', '-' * 30, '\n')

        #
        # ___________________ check user balance

        user_account_details = get_user_account_details(api_key, client)

        if type(user_account_details) is dict:

            _update_bot_status(user_id, slot, "Checking Balance & User's Conditions")

            user_balance = float(user_account_details['account']['balance'])
            log_creator(user_id, slot, f"user's balance checked", state_write=3)

        else:
            print('user account connection fail')
            log_creator(user_id, slot, f'user account connection fail : {user_account_details}', 0, 3)
            sleep(5)
            continue

        if user_balance <= 0:
            print("user's balance not enought to creat order")
            log_creator(user_id, slot, "user's balance not enought to creat order", 0)

            _update_bot_status(user_id, slot, "user's balance not enought to creat order", mode=0)
            # sent_mail(user_id, slot)
            exit(0)

        #
        # ___________________ check maximum unit

        maximum_unit = calculate_maximum_unit(api_key, client, symbol)
        if type(maximum_unit) is int:
            if unit_1 > maximum_unit:
                print("can't create order with more than maximum unit")
                log_creator(user_id, slot, "can't create order with more than maximum unit", 0)

                _update_bot_status(user_id, slot, "can't create order with more than maximum unit", mode=0)
                # sent_mail(user_id, slot)
                exit(0)

            else:
                pass

        else:
            sleep(5)
            continue

        #
        # ___________________ check market trainds

        symbol_pack, forex_predict_pack = get_forex_predict()

        if symbol not in symbol_pack:
            forex_predict = 0

        else:
            forex_predict = float(forex_predict_pack[symbol])

        #
        # ___________________ check instrument price

        sell_price, buy_price = ask_prices(api_key, client, symbol)

        if not sell_price:
            log_creator(user_id, slot, f"get {symbol!r} market price error : {buy_price}", 0)

            _update_bot_status(user_id, slot, f"get {symbol!r} market price error / Re - Getting")
            sleep(5)
            continue

        log_creator(user_id, slot, "market trainds & instrument price checked")

        #
        # ___________________ calculate stop loss price and take profit price

        if int(pips_sl_1) % 1 == 0 and int(pips_tp_1) % 1 == 0:

            _update_bot_status(user_id, slot, 'Calculate Stop Loss and Take Profit')

            if forex_predict > 0:   # or (forex_predict == 0 and spare_first_order_type is 'buy'):
                stop_loss_1, take_profit_1 = calculate_stop_lose_or_take_profit_point(buy_price, pips_sl_1,
                                                                                      pips_tp_1, 0)

                first_order_history = 'b'

            elif forex_predict < 0:
                stop_loss_1, take_profit_1 = calculate_stop_lose_or_take_profit_point(sell_price, pips_sl_1,
                                                                                      pips_tp_1, 1)

                first_order_history = 's'

            else:
                if spare_first_order_type is 'buy':
                    stop_loss_1, take_profit_1 = calculate_stop_lose_or_take_profit_point(buy_price, pips_sl_1,
                                                                                          pips_tp_1, 0)

                    first_order_history = 'b'

                else:
                    stop_loss_1, take_profit_1 = calculate_stop_lose_or_take_profit_point(sell_price, pips_sl_1,
                                                                                          pips_tp_1, 1)

                    first_order_history = 's'

            print(f"Stop Loss = {stop_loss_1}, Take Profit = {take_profit_1}")

            log_creator(user_id, slot, "calculate stop loss price and take profit price finished")

        else:
            print('pips must be integer')
            log_creator(user_id, slot, "pips must be integer", 0)

            _update_bot_status(user_id, slot, 'Pips must be Integer!!!')
            sleep(5)
            continue

        # -------------------------------------------------------------------------------------------------------------
        # -------------------- STATE IV : Create First Order ----------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        print('\n', '-' * 30, 'STATE IV', '-' * 30, '\n')

        if not unit_1 or unit_1 is '0' or unit_1 == 0:
            log_creator(user_id, slot, "unit is null or 0", 0, 4)

            _update_bot_status(user_id, slot, "unit is null or 0", mode=0)
            # sent_mail(user_id,  slot)
            exit(0)

        if int(unit_1) % 1 != 0:
            log_creator(user_id, slot, "unit must be integer", 0, 4)

            _update_bot_status(user_id, slot, "unit must be integer", mode=0)
            # sent_mail(user_id, slot)
            exit(0)

        _update_bot_status(user_id, slot, 'Creating First Order')

        if first_order_history == 's':

            print('First Order is Sell Order')
            status, first_trade_id = sell_by_limit(api_key, client, symbol, unit_1, sell_price, stop_loss_1,
                                                   take_profit_1)

        else:

            print('First Order is Buy Order')
            status, first_trade_id = buy_by_limit(api_key, client, symbol, unit_1, buy_price, stop_loss_1,
                                                  take_profit_1)

        if not status:
            log_creator(user_id, slot, f"Create first order fail by {first_trade_id}", 0, 4)

            _update_bot_status(user_id, slot, f"Create first order fail by {first_trade_id}", mode=0)
            # sent_mail(user_id, slot)
            # exit(0)
            continue

        print(f"First order created with {first_order_history} order, trade_id : {first_trade_id}")

        log_creator(user_id, slot,
                    f"First order created with {first_order_history.capitalize()!r} order, trade_id : {first_trade_id}",
                    state_write=4)

        # sent_mail(user_id, slot, amount=unit_1, symbol=symbol, side=first_trade_id)

        _update_bot_status(user_id, slot, 'First Order Created')

        sql = f"INSERT INTO trading_history (datetime, user_id, method, exchange, side, order_id, symbol, amount,"\
            f" price, cost, status, note, profit, profit_percentage, first_order_id) "\
            f"VALUES('{strftime('%D %H:%M:%S')}', '{user_id}', '{'1'}', '{'oanda'}',"\
            f" '{'SELL' if first_order_history is 's' else 'BUY'}', '{first_trade_id}', '{symbol}', '{unit_1}',"\
            f" '{sell_price if first_order_history is 's' else buy_price}', '{0}', '{'new'}', '{'first_order'}',"\
            f" '{''}', '{''}', '{''}')"

        update_trade_history(sql)

        # -------------------------------------------------------------------------------------------------------------
        # -------------------- STATE V : Check User's Trade Status ----------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------

        print('\n', '-' * 30, 'STATE V', '-' * 30, '\n')

        while_loop = 0

        while True:

            bot_status = check_switch(user_id, slot)

            if bot_status == 'off':
                close_order(api_key, client, first_trade_id)
                close_bot(user_id, slot)
                exit(0)

            order_list = call_order_list(api_key, client, symbol)

            if type(order_list) is list:
                if order_list:
                    if while_loop == 0:

                        log_creator(user_id, slot, "First order is still trading", state_write=5)
                        # _update_bot_status(user_id, slot, "First order is still trading")

                    elif while_loop % 20 == 0:

                        log_creator(user_id, slot, "First order is still trading")
                        # _update_bot_status(user_id, slot, "First order is still trading")

                else:
                    pass
            else:
                log_creator(user_id, slot, f"Check first order fail by {first_trade_id}", 0, 5)
                sleep(5)
                continue

            if first_trade_id not in order_list:

                print(f"Trade ID {first_trade_id} with {symbol} instrument is closed already")
                log_creator(user_id, slot, f"Trade ID {first_trade_id} with {symbol} instrument is closed already")

                break

            else:
                trade_detail = get_trade_details(api_key, client, first_trade_id)
                _update_bot_status(user_id, slot, trade_detail)
                print(strftime('%D %H:%M:%S'), ' | ', trade_detail)

                if type(trade_detail) is str:
                    if while_loop == 0 or while_loop % 20 == 0:
                        log_creator(user_id, slot, trade_detail)

                    while_loop += 1
                    sleep(15)

                else:
                    print(f"trade_detail error : {trade_detail[1]}")
                    log_creator(user_id, slot, trade_detail[1], sign=0)

        # -------------------------------------------------------------------------------------------------------------
        # -------------------- STATE VI : Check Order Closed Transaction Reason and Create Summaries ------------------
        # -------------------------------------------------------------------------------------------------------------

        sleep(30)

        print('\n', '-' * 30, 'STATE VI', '-' * 30, '\n')

        transaction_reason, profit_loss = get_transaction_details(api_key, client, first_trade_id)

        sql = f"UPDATE {'trading_history'} SET {'note'} = '{'first_order'}_{transaction_reason}', {'status'} ="\
            f" '{'filled'}', profit = '{profit_loss}' WHERE order_id = '{first_trade_id}'"

        update_trade_history(sql)

        act = 'Order Closed by User' if transaction_reason == 'ON_FILL' else f'Order closed by {transaction_reason}'
        _update_bot_status(user_id, slot, act)

        if transaction_reason is not False:

            # sent_mail(user_id, slot, amount=unit_1, symbol=symbol, side=first_trade_id)

            if transaction_reason == 'STOP_LOSS_ORDER':
                print(f'Trade ID {first_trade_id} is closed by {transaction_reason}')

                log_creator(user_id, slot, f'Trade ID {first_trade_id} is closed by {transaction_reason}',
                            state_write=6)

            elif transaction_reason == 'TAKE_PROFIT_ORDER':
                print(f'Trade ID {first_trade_id} is closed by {transaction_reason}')
                # second_order_state = 1  # second order is cross from first order

                log_creator(user_id, slot, f'Trade ID {first_trade_id} is closed by {transaction_reason}',
                            state_write=6)

            elif transaction_reason == 'ON_FILL':
                print('user closed order form website by themselves')
                log_creator(user_id, slot, 'user closed order form website by themselves', state_write=6)

                _update_bot_status(user_id, slot, 'user closed order form website by themselves')

                close_order(api_key, client, first_trade_id)
                close_bot(user_id, slot)
                exit(0)

            else:
                print(f'Trade ID {first_trade_id} is closed by {transaction_reason}')
                log_creator(user_id, slot, f'Trade ID {first_trade_id} is closed by {transaction_reason}',
                            state_write=6)

                _update_bot_status(user_id, slot, f'Order Created by {transaction_reason}')

                close_order(api_key, client, first_trade_id)
                close_bot(user_id, slot)
                exit(0)

        else:
            sleep(5)
            continue

        # -------------------------------------------------------------------------------------------------------------
        # -------------------- STATE VII : Check Conditions for Second Order from User's config -----------------------
        # -------------------------------------------------------------------------------------------------------------

        # print('\n', '-' * 30, 'STATE VII', '-' * 30, '\n')


# forex_mi_main('409', '1')
