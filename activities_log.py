
import os
from time import strftime, localtime


def log_creator(user_id, slot, msg, sign=1, state_write=None, header=None):

    sign_msg = {0: u'\u2716', 1: u'\u2714'}

    log_dict = {0: 'STATE 0 : Loss Orders In Continuously',
                1: 'STATE I : Get User Config from Database',
                2: 'STATE II : Generate API Client from User id and token',
                3: 'STATE III : Check Conditions for First Order from User\'s config',
                4: 'STATE IV : Create First Order',
                5: 'STATE V : Check User\'s Trade Status',
                6: 'STATE VI : Check Order Closed Transaction Reason and Create Summaries',
                7: 'STATE VII : Check Conditions for Second Order from User\'s config',
                8: 'STATE VIII : Create Second Order if First Order take stop loss'}

    if not os.path.exists('LOG'):
        os.makedirs('LOG')

    log_name = os.path.join('NUEVE_LOG', f"{user_id}_{slot}_log.txt")
    file = open(log_name, "a")

    if header:
        file.write(f"\n\n\n\n{'*'*100}\n")
        file.write(f"{'*'*100}\n")
        file.write(f"\nUser_ID : {user_id}\nBot Slot Number : {slot}")
        file.write(f"\n{msg}\n\n")
        file.write("Bot Activities : ")

    else:
        if state_write:
            file.write(f"\n\n\n--------------------  {log_dict[state_write]:^75s}  --------------------\n")

        file.write(f"\n  [{strftime('%Y-%m-%d %H:%M:%S', localtime())}] -- [{sign_msg[sign]}]  ==========>>  {msg}\n")

    file.close()

