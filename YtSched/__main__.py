from . import *
from . import a

class A:
    def __init__(self):
        self.logger = get_logger(__class__.__name__, True)
        self.logger.debug('')

        self.o = a.A(debug=True)
        
    def main(self, b):
        self.logger.debug('b=%d', b)
        print(self.o.func1(b))

if __name__ == '__main__':
    obj = A()
    obj.main(3)
    
