import time
import configargparse
from ai.blueprint import Blueprint


def run():
    """
     Start blueprint
    """
    blueprint = Blueprint()
    start_time = time.time()
    blueprint.run()
    end_time = time.time()
    time_delta = end_time - start_time
    print('Finished in ' + str(int(time_delta)) + ' sec.')


if __name__ == '__main__':
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--pairs', help='Pairs to backfill. For ex. [BTC_ETH, BTC_* (to get all BTC_* prefixed pairs]')
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='mosquito.ini')
    run()
