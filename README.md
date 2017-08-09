<img src="https://user-images.githubusercontent.com/1301154/28501904-86816828-6fe6-11e7-81a0-73c7d6afe5d5.png" width="480">

Flexible Trading Bot with main focus on Machine Learning and Genetic Algorithms, inspired by [zenbot](https://github.com/carlos8f/zenbot)

[![Build Status](https://travis-ci.org/miti0/mosquito.svg?branch=master)](https://travis-ci.org/miti0/mosquito)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d037c01ffa2441118ae709efeaae34b1)](https://www.codacy.com/app/miti0/mosquito?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=miti0/mosquito&amp;utm_campaign=Badge_Grade)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/mosquito-bot/Lobby)


## About
Mosquito is a crypto currency trading bot writen in Python, with main focus on modularity, 
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
 * Python 3.*
 * mongodb
 * Depending on the exchange you want to use:
   * [Poloniex-api](https://github.com/s4w3d0ff/python-poloniex)
   * [Bittrex-api](https://github.com/miti0/python-bittrex)



## Quick Start



### Install
 1. clone repo
 ```
 git clone https://github.com/miti0/mosquito.git
 ```
 2. install mongodb & required python packages
 
 3. set-up config.ini (if you want to use sample config, just rename config.sample.ini to config.ini)
 
 3. Run desired command (full list of commands below)
 


## Backfill
Backfill gets history data from exchange and stores them to mongodb. Data can be after that used for testing your simulation strategies.

```
usage: mosquito.py [-h] [--backtest] [--paper] [--live] [--strategy STRATEGY] [--plot]

optional arguments:
  -h, --help           show this help message and exit
  --backtest           Simulate your strategy on history ticker data
  --paper              Simulate your strategy on real ticker
  --live               REAL trading mode
  --strategy STRATEGY  Name of strategy to be run (if not set, the default one will be used
  --plot               Generate a candle stick plot at simulation end

```

Example below load historical data for BTC_ETH pair for the last 5 days
```
python3 backfill --days 5 --pair BTC_USD
```

Example below load historical data for ALL pairs for the last 2 days
```
python3 backfill --days 3 --all
```


## Trading
This is the main module that handles passed strategy and places buy/sell orders. 

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
python3 mosquito.py --paper
```
> ! Please be aware that Paper should 99% work, but it is currently under final verification test.


### Live
Live trading with placing REAL buy/sell orders. Configuration is done via *config.ini* file (some of the parameters can be overridden with command line arguments).
Below is an example of running a backtest together with final buy/sell plot generated at the end of the simulation.
```
python3 mosquito.py --live
```
> ! Please be aware that Live should 99% work, but it is currently under final verification test.



## Plot and Statistics
Mosquito has a simple plot utility for visualizing current pair combined with trading history. 
Visualization uses external library [plotly](https://plot.ly/). Below You can see an example visualizing ticker price plot, together with simulated buy/sell orders.

<img src="https://user-images.githubusercontent.com/1301154/28573699-70c6d14c-7119-11e7-8bb6-06c53908066d.png">

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
Created new window in existing browser session.
```


## Donate
If you would like to support the project in other way than code-contributing, you can donate Mosquito development on 
following Bitcoin address:

16v94untkyuTXyE4euWzDA5r4vKd996CP8

---



### License: GNU GENERAL PUBLIC LICENSE
- Copyright (C) 2017 Miroslav Karpis (miti0)


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
