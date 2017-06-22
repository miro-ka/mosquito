import argparse
from core.engine import Engine



def main(args):

    engine = Engine(args, 'config.ini')
    engine.run()




if __name__ == "__main__":

    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action='store_true')
    parser.add_argument("--paper", help="Simulate your strategy on real ticker", action='store_true')
    parser.add_argument("--trade", help="REAL trading mode", action='store_true')
    parser.add_argument("--strategy", help="Name of strategy to be run (if not set, the default one will be used")

    args = parser.parse_args()

    main(args)

