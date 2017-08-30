import configargparse
from ai.blueprint import Blueprint


def run():
    """
     Start blueprint
    """
    blueprint = Blueprint()
    blueprint.run()


if __name__ == '__main__':
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='mosquito.ini')
    run()
