from . import *
from . import a

import click

#####
class B:
    def __init__(self, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('aaa')

        self.a = a.A(debug=self.debug)

    def main(self, a):
        self.logger.debug('a=%d', a)
        
        self.logger.info(self.a.func1(a))

#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('a', type=int, default=1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(a, debug):
    logger = get_logger('', debug)
    logger.info('a=%d', a)

    obj = B(debug=debug)
    obj.main(a)

if __name__ == '__main__':
    main()
