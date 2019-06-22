print(__name__)
from . import *

#####
class Sample:
    def __init__(self, year, month, day, dirname, debug=False):
        self.debug = debug
        self.logger = mylogger.get_logger(__class__.__name__, self.debug)
        self.logger.debug('')

        self.year  = year
        self.month = month
        self.day   = day

        self.o = a.A(debug=self.debug)
        
    def main(self):
        self.logger.debug('')
        print(self.o.func1(3))

    def end(self):
        self.logger.debug('')
