import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
logging.basicConfig(filename='.\\logs.log', level=logging.INFO, datefmt='%m/%d/%Y %I:%M %p', format='[%(asctime)s %(filename)s %(funcName)s():%(lineno)s] %(levelname)s: %(message)s')

class whoa:
    def __init__(self) -> None:
        logging.info(f'setup {__class__}')
    
    def go(self):
        logging.info(f'setup {__class__}')

f = whoa()
f.go()
# Get the previous frame in the stack, otherwise it would
# be this function!!!
# func = inspect.currentframe().f_back.f_code
# # Dump the message + the name of this function to the log.
# logging.info("%s: %s in %s:%i" % (
#     "test message", 
#     func.co_name, 
#     func.co_filename, 
#     func.co_firstlineno
# ))