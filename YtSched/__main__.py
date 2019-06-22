print(__name__)
from . import *
#####
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('year', type=int, default=2019)
@click.argument('month', type=int, default=1)
@click.argument('day', type=int, default=1)
@click.option('--data-dir', '--dir', 'dirname', type=click.Path(), default='',
              help='data directory')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(year, month, day, dirname, debug):
    logger = mylogger.get_logger(__name__, debug)
    logger.info('%d/%d/%d', year, month, day)
    logger.info('dirname=%s', dirname)
    logger.info('debug=%s', debug)

    obj = Sample.Sample(year, month, day, dirname, debug=debug)
    try:
        obj.main()
    finally:
        obj.end()

if __name__ == '__main__':
    main()
