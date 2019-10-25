
import sys
from time import localtime, strftime
from datetime import datetime, timedelta
from mysql.connector import errorcode, Error, connect


def connect_2_database(db_select=0):

    if db_select == 0:

        config = {
            'user': '',
            'password': '',
            'host': '',
            'database': '',
            'charset': 'utf8mb4'
        }

    else:

        config = {
            'user': '',
            'password': '',
            'host': '',
            'database': '',
            'charset': ''
        }

    try:
        cnx = connect(**config)

    except Error as err:

        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Something wrong with your user name or password')

        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")

    else:
        return cnx


def get_forex_predict():

    cnx = connect_2_database(1)
    cur = cnx.cursor(buffered=True)

    current_date = strftime("%Y-%m-%d", localtime())

    query = f"SELECT symbol, sentiment_score, predicted_price FROM `{current_date}`"
    # query = f"SELECT symbol, sentiment_score FROM `{current_date}`"

    print(f">>>>> find forex prediction from {current_date!r}")

    try:
        cur.execute(query)

        requests = ([(record[0], record[1], record[2]) for record in cur.fetchall()])
        request = ([(record[0].replace(record[0][:3], f"{record[0][:3]}_"), record[1]) for record in requests])
        # predicted_price = [(rec[0], rec[2]) for rec in requests]
        instrument_pack = [inst[0] for inst in request]

        # print(request)
        # print(predicted_price)
        # print(instrument_pack)

        return instrument_pack, dict(request)

    except Error as err:

        if err.errno == errorcode.ER_NO_SUCH_TABLE:

            current_day = datetime.today().weekday()

            if current_day == 0:
                trowback_date = datetime.strftime(datetime.now() - timedelta(3), '%Y-%m-%d')

            else:
                trowback_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

            print(f">>>>> forex prediction for {current_date!r} doesn't exist, find from {trowback_date!r} instead")

            query = f"SELECT symbol, sentiment_score, predicted_price FROM `{trowback_date}`"

            try:
                cur.execute(query)

                requests = ([(record[0], record[1], record[2]) for record in cur.fetchall()])
                request = ([(record[0].replace(record[0][:3], f"{record[0][:3]}_"), record[1]) for record in requests])
                # predicted_price = [(rec[0], rec[2]) for rec in requests]
                instrument_pack = [inst[0] for inst in request]

                # print(request)
                # print(predicted_price)
                # print(instrument_pack)

                return instrument_pack, dict(request)

            except Error as error:
                print(f'SQL queries error, type : {error}')
                pass

        else:
            print(f'SQL queries error, type : {err}')

            return None, None

    finally:
        if cur:
            cur.close()

        if cnx:
            cnx.close()


def get_forex_and_pirce_predict():

    cnx = connect_2_database(1)
    cur = cnx.cursor(buffered=True)

    current_date = strftime("%Y-%m-%d", localtime())

    query = f"SELECT symbol, sentiment_score, predicted_price FROM `{current_date}`"

    print(f">>>>> find forex prediction from {current_date!r}")

    try:
        cur.execute(query)

        requests = ([(record[0], record[1], record[2]) for record in cur.fetchall()])
        request = ([(record[0].replace(record[0][:3], f"{record[0][:3]}_"), record[1]) for record in requests])
        predicted_price = [(rec[0], rec[2]) for rec in requests]
        instrument_pack = [inst[0] for inst in request]

        # print(dict(request))
        # print(dict(predicted_price))
        # print(instrument_pack)

        return instrument_pack, dict(request), dict(predicted_price)

    except Error as err:

        if err.errno == errorcode.ER_NO_SUCH_TABLE:
            print('forex trainds predict for today is not avaliable now.')
            return 'forex trainds predict for today is not avaliable now.', 'not_avaliable', False

        else:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            template = "Exception In DB Connect type {0}. in Line {2}"
            message = template.format(err, exc_tb.tb_lineno)
            print(message)
            return message, False, False

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        template = "Exception type {0}. Arguments:\n{1!r} in Line {2}"
        message = template.format(type(ex).__name__, ex.args, exc_tb.tb_lineno)
        print(message)
        return message, False, False

    finally:
        if cur:
            cur.close()

        if cnx:
            cnx.close()


def update_trade_history(sql_command):

    try:
        cnx = connect_2_database()
        cur = cnx.cursor()

        cur.execute(sql_command)
        cnx.commit()

        if cur:
            cur.close()
        if cnx:
            cnx.close()

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        template = "Exception type {0}. Arguments:\n{1!r} in Line {2}"
        message = template.format(type(ex).__name__, ex.args, exc_tb.tb_lineno)
        print(message)
        pass


def _update_bot_status(user_id, slot, status, mode=1):

    status = status.replace("'", "\''")

    if mode == 0:

        sql_command = f"UPDATE {'FOREX_setting'} SET bot_switch = '{'on'}', bot_state = '{'0'}'," \
            f" bot_massage = '{status}', bot_active = '{strftime('%Y-%m-%d %H:%M:%S')}' WHERE user_id = '{user_id}' " \
            f"AND slot = '{slot}'"

    else:
        sql_command = f"UPDATE {'FOREX_setting'} SET bot_massage = '{status}', bot_active = " \
            f"'{strftime('%Y-%m-%d %H:%M:%S')}' WHERE user_id = '{user_id}' AND slot = '{slot}'"

    try:
        cnx = connect_2_database()
        cur = cnx.cursor()

        cur.execute(sql_command)
        cnx.commit()

        if cur:
            cur.close()
        if cnx:
            cnx.close()

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        template = "Exception type {0}. Arguments:\n{1!r} in Line {2}"
        message = template.format(type(ex).__name__, ex.args, exc_tb.tb_lineno)
        print(message)


def check_switch(user_id, slot):
    my_db = connect_2_database()
    cur = my_db.cursor()

    query_result = False

    try:
        sql = f"SELECT bot_switch FROM FOREX_setting WHERE user_id = '{user_id}' AND slot = '{slot}'"

        cur.execute(sql)
        query_result = cur.fetchone()

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        template = "Exception type {0}. Arguments:\n{1!r} in Line {2}"
        message = template.format(type(ex).__name__, ex.args, exc_tb.tb_lineno)
        print(message)

        pass

    else:
        cur.close()
        my_db.close()

    return query_result


def close_bot(user_id, slot):
    my_db = connect_2_database()
    cur = my_db.cursor()

    query_result = False

    try:

        sql_update = f"UPDATE FOREX_setting SET bot_state = '{'0'}' WHERE user_id = '{user_id}' AND slot = '{slot}'"
        cur.execute(sql_update)
        my_db.commit()

    except Exception as ex:
        template = "sql update error : {0}. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    else:
        cur.close()
        my_db.close()

    return query_result
