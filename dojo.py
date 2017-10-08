import time
import configargparse
from dojo.dojo import Dojo


def run():
    """
     Start blueprint
    """
    dojo = Dojo()
    start_time = time.time()
    args = arg_parser.parse_known_args()[0]
    dojo.train(blueprint=args.blueprint)
    end_time = time.time()
    time_delta = end_time - start_time
    print('Finished in ' + str(int(time_delta)) + ' sec.')


if __name__ == '__main__':
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-v', '--verbose', help='Verbosity', action='store_true')
    arg_parser.add('-b', '--blueprint', help='blueprint csv.file')
    run()
