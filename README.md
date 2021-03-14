<img src="https://user-images.githubusercontent.com/1301154/28501904-86816828-6fe6-11e7-81a0-73c7d6afe5d5.png" width="480">

Flexible Trading Bot with main focus on Machine Learning and Genetic Algorithms, inspired by [zenbot.](https://github.com/carlos8f/zenbot)

[![Build Status](https://travis-ci.org/miro-ka/mosquito.svg?branch=master)](https://travis-ci.org/miro-ka/mosquito)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d037c01ffa2441118ae709efeaae34b1)](https://www.codacy.com/app/miti0/mosquito?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=miti0/mosquito&amp;utm_campaign=Badge_Grade)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/mosquito-bot/Lobby)
[![codebeat badge](https://codebeat.co/badges/46a04bf1-ce92-41ad-84ba-6627e08f54d5)](https://codebeat.co/projects/github-com-miti0-mosquito-master)

## About
Mosquito is a crypto currency trading bot written in Python, with main focus on modularity,
so it is straight forward to plug-in new exchange.

The idea to build a new bot came because of I was missing following easy-access features in all of available bots
available at the time mid 2017:
 * **Multi-currency bot** - Be able to monitor and exchange several currencies in one strategy (no need to run 5 same strategies for 5 different currencies).
 * **Easy AI plug** - Possibility to easily plug any of the existing AI/ML libraries (for ex. scikit or keras)

> **Please be AWARE that Mosquito is still in beta and under heavy development. Please use it in Live trading VERY carefully.**

### Supported Exchanges
Mosquito currently supports following exchanges:
 * **Poloniex** - supporting *fillOrKill* and *immediateOrCancel* trading types. *postOnly* type is not supported. You can
 read more about trading types [here.](https://github.com/s4w3d0ff/python-poloniex/blob/master/poloniex/__init__.py)
 * **Bittrex** - supporting *Trade Limit Buy/Sell Orders*


## Requirements
 * Python 3.8
 * mongodb
 * Depending on the exchange you want to use:
   * [Poloniex-api](https://github.com/s4w3d0ff/python-poloniex)
   * [Bittrex-api](https://github.com/miti0/python-bittrex)



## Quick Start



### Install
 1. Clone repo
 ```
 git clone https://github.com/miti0/mosquito.git
 ```
 2. Install requirements (ideally in separate virtual environment)
 ```
 pip install -r requirements.txt
 ```
 3. Install [mongodb](https://www.mongodb.com/try/download/community) 

 4. Set-up mosquito.ini (if you want to use sample config, just rename mosquito.sample.ini to mosquito.ini)

 5. Run desired command (full list of commands below)

 All parameters in the program can be overridden with input arguments.
 You can get list of all available arguments with:

```
 python mosquito.py --help
```


## Backfill
Backfill gets history data from exchange and stores them to mongodb. Data can be after that used for testing your simulation strategies.

usage: backfill.py [-h] [--pairs PAIRS] [--all] --days DAYS

```
optional arguments:
  -h, --help   show this help message and exit
  --pairs PAIRS PairS to backfill. For ex. [BTC_ETH, BTC_* (to get all BTC_*
               prefixed pairs]
  --all        Backfill data for ALL currencies
  --days DAYS  Number of days to backfill
```


Example 1) Load historical data for BTC_ETH pair for the last 5 days:
```
python backfill.py --days 5 --pairs BTC_USD
```

Example 2) Load historical data for ALL pairs for the last 2 days
```
python backfill.py --days 3 --all
```

Example 3) Load historical data for all pairs starting with BTC_ for the last day
```
python backfill.py --days 1 --pairs BTC_*
```



## Trading
This is the main module that handles passed strategy and places buy/sell orders.

 Architecture and logic of mosquito is made so, that it should be easy to set and tune all strategy parameters with program arguments. Below is a list of main arguments that can be either configured via the mosquito.ini config file or by passing the value/values as argument.

```
-h, --help            show this help message and exit
 --polo_api_key POLO_API_KEY
                       Poloniex API key (default: None)
 --polo_secret POLO_SECRET
                       Poloniex secret key (default: None)
 --polo_txn_fee POLO_TXN_FEE
                       Poloniex txn. fee (default: None)
 --polo_buy_order POLO_BUY_ORDER
                       Poloniex buy order type (default: None)
 --polo_sell_order POLO_SELL_ORDER
                       Poloniex sell order type (default: None)
 --bittrex_api_key BITTREX_API_KEY
                       Bittrex API key (default: None)
 --bittrex_secret BITTREX_SECRET
                       Bittrex secret key (default: None)
 --bittrex_txn_fee BITTREX_TXN_FEE
                       Bittrex txn. fee (default: None)
 --exchange EXCHANGE   Exchange (default: None)
 --db_url DB_URL       Mongo db url (default: None)
 --db_port DB_PORT     Mongo db port (default: None)
 --db DB               Mongo db (default: None)
 --pairs PAIRS         Pairs (default: None)
 --use_real_wallet     Use/not use fictive wallet (only for paper simulation)
                       (default: False)
 --backtest_from BACKTEST_FROM
                       Backtest epoch start datetime (default: None)
 --backtest_to BACKTEST_TO
                       Backtest epoch end datetime (default: None)
 --backtest_days BACKTEST_DAYS
                       Number of history days the simulation should start
                       from (default: None)
 --wallet_currency WALLET_CURRENCY
                       Wallet currency (separated by comma) (default: None)
 --wallet_amount WALLET_AMOUNT
                       Wallet amount (separated by comma) (default: None)
 --backtest            Simulate your strategy on history ticker data
                       (default: False)
 --paper               Simulate your strategy on real ticker (default: False)
 --live                REAL trading mode (default: False)
 --plot                Generate a candle stick plot at simulation end
                       (default: False)
 --ticker_size TICKER_SIZE   Simulation ticker_size (default: 5)
 --root_report_currency ROOT_REPORT_CURRENCY
                       Root currency used in final plot (default: None)
 --buffer_size BUFFER_SIZE
                       Buffer size in days (default: 30)
 --prefetch            Prefetch data from history DB (default: False)
 --plot_pair PLOT_PAIR
                       Plot pair (default: None)
 --all ALL             Include all currencies/tickers (default: None)
 --days DAYS           Days to pre-fill (default: None)
 -c CONFIG, --config CONFIG
                       config file path (default: mosquito.ini)
 -v, --verbosity       Verbosity (default: False)
 --strategy STRATEGY   Strategy (default: None)
 --fixed_trade_amount FIXED_TRADE_AMOUNT
                       Fixed trade amount (default: None)

```

Currently Trading supports following modes:
 * **Backtest** - fast simulation mode using past data and placing fictive buy/sell orders.
 * **Paper** - mode simulating live ticker with placing fictive buy/sell orders.
 * **Live** - live trading with placing REAL buy/sell orders.

> Backtest and Paper trading are using immediate buy/sell orders by using the last ticker
closing price. This results to NOT 100% accurate strategy results, what you should be aware of.


### Backtest
Fast simulation mode using past data and placing fictive buy/sell orders. Simulation configuration is done via
*config.ini* file (some of the parameters can be overridden with command line arguments).

Below is an example of running a backtest together with final buy/sell plot generated at the end of the simulation.
```
python3 mosquito.py --backtest --plot
```
> ! Please be aware that Backtest should 99% work, but it is currently under final verification test.


### Paper
Trading mode that simulates live ticker with placing fictive buy/sell orders. Simulation configuration is done via
*config.ini* file (some of the parameters can be overridden with command line arguments).

Below is an example of running a backtest together with final buy/sell plot generated at the end of the simulation.
```
python mosquito.py --paper
```
> ! Please be aware that Paper should 99% work, but it is currently under final verification test.


### Live
Live trading with placing REAL buy/sell orders. Configuration is done via *config.ini* file (some of the parameters can be overridden with command line arguments).
Below is an example of running a backtest together with final buy/sell plot generated at the end of the simulation.
```
python mosquito.py --live
```
> ! Please be aware that Live should 99% work, but it is currently under final verification test.



## Plot and Statistics
Mosquito has a simple plot utility for visualizing current pair combined with trading history.
Visualization uses external library [plotly](https://plot.ly/). Below You can see an example visualizing ticker price plot, together with simulated buy/sell orders.

<img src="https://user-images.githubusercontent.com/1301154/29753922-68696196-8b7b-11e7-9fc6-c2d7c1e9b42f.png">

Below is an example of Final Simulation Report summary:
```
****************************************************
              Final simulation report:               
****************************************************
Wallet at Start: | 50.0DGB |
Wallet at End: | 51.3464723121DGB |
Strategy result: -5.68%
Buy & Hold: -8.16%
Strategy vs Buy & Hold: 2.47%
Total txn: 10
Simulated (data time): 0 days, 4 hours and 55 minutes
Transactions per hour: 2.03
Simulation run time: 0 hours 1 minutes and 13 seconds
```

## AI

### Blueprint
Blueprint is a part of AI package. Main function of the module is to generate datasets which can be used for training AI. Logic of Blueprint module is following:

 1. Create a blueprint file/module which contains features, indicators and output parameters. As an example you can take a look at ai/blueprints/minimal.py or ai/blueprints/junior.py

 2. Decide how many days you would like to run the Blueprint. Backfill data for that period.

 3. Choose which pair/pairs you would like to include. Following combinations should work [BTC_ETH] - single pair, [BTC_ETH, BTC_LTC] - list of pairs, [BTC_*] - all pairs with prefix BTC

 4. Start blueprint with following parameters (example below)

```
python blueprint.py --features junior --days 200
```

As a result you should see *.csv file in your Mosquito's **out/blueprints** folder, which should contain the dataset.


## Utilities

### Wallet Lense 
Simple module which sends up to 24h winners/losers market pairs summary by email in user specified intervals (sample below).
 
<img src="https://user-images.githubusercontent.com/1301154/33880555-4b385b08-df32-11e7-8208-34cd4374aeff.png" width="371">

#### Usage
```
# You need to have configured email parameters in ini file, or pass them as input arguments.
python lense.py 
```



## Donate
If you would like to support the project in other way than code-contributing, you can donate Mosquito development on
following Bitcoin address:

3QK7MXUQfnWHqGPQePtTsen5m1jQ4MfUTJ

---



### License: GNU GENERAL PUBLIC LICENSE
- Copyright (C) 2021 Miro Karpis (miro-ka)


  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.


THE SOFTWARE IS PROVIDED &quot;AS IS&quot;, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
