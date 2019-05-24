from . import *
from . import a

#####
class Sample:
    def __init__(self, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('')

        self.o = a.A(debug=self.debug)
        
    def main(self):
        self.logger.debug('')
        print(self.o.func1(3))

    def end(self):
        self.logger.debug('')

#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('a', type=int, default=1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(a, debug):
    logger = get_logger(__name__, debug)
    logger.info('a=%d, debug=%s', a, debug)

    obj = Sample(debug=debug)
    try:
        obj.main()
    finally:
        obj.end()

if __name__ == '__main__':
    main()
    
