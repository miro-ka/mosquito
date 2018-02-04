import time
import configargparse
from exchanges.exchange import Exchange


def test_trade_history():
    """
    Gets sample trades history
    """
    exchange = Exchange()
    end = time.time()
    start = end - 3600
    data = exchange.get_market_history(start=start,
                                       end=end,
                                       currency_pair='BTC_ETH')
    print(data)


if __name__ == "__main__":
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='../mosquito.ini')
    options = arg_parser.parse_known_args()[0]

    test_trade_history()
