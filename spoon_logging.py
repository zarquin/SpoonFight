"""Utility.py all the logging you need"""

import logging
import datetime

#TODO make this work
now_str = datetime.datetime.now().strftime("%y%m%d-%H%M%S") #time.time()

# make a formatter
formatter = logging.Formatter('%(levelname)s-%(threadName)s-%(filename)s-%(funcName)s-%(message)s')

#TODO make this respond to startup arguments
logging.basicConfig(filename="{}-spoonFight.log".format(now_str), 
                    level=logging.INFO,
                    format="%(levelname)s:%(threadName)s:%(filename)s:%(funcName)s:%(message)s")
#logging.getLogger().addHandler(logging.StreamHandler())

# convenience functions
D = logging.debug
L = logging.info
W = logging.warning
E = logging.error
 
