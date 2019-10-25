
"""
 Last Update : 15/07/2019
 Note : Update print(massage)/Function check max profit

 This is sample code for my Auto Forex Trader on Oanda Bot


 I have complete code and more trade mode such as 3 state's profit guarantee,
 hyena scraping profit, morning star and evening star pattern trade etc.


 If you interested in this project, You can contact me.


 E-Mail : 5735512155@psu.ac.th
 LinkedIn : https://www.linkedin.com/in/jakgri-klabdi-1b5557183/

"""

# ---------------------------------------------------------------------------------------------------------------------

import time
import multiprocessing

from mode_I import forex_mi_main
# from mode_II import forex_mii_main


mode = 1    # 1 or 2

if mode == 1:
    process = multiprocessing.Process(target=forex_mi_main)

else:

    # process = multiprocessing.Process(target=forex_miI_main)
    process = multiprocessing.Process(target=forex_mi_main)

process.start()
time.sleep(5)
