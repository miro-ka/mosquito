# mosquito
Flexible Trading Bot with main focus on Machine Learning and Genetic Algorithms, inspired by [zenbot](https://github.com/carlos8f/zenbot)

[![Build Status](https://travis-ci.org/miti0/mosquito.svg?branch=master)](https://travis-ci.org/miti0/mosquito)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/5609393e38ed496cbd166cdb7b0c019e/badge.svg)](https://www.quantifiedcode.com/app/project/5609393e38ed496cbd166cdb7b0c019e)


## About
Mosquito is a crypto currency trading bot writen in Python, with main focus on modularity, so it is straight forward to plug-in new exchange. 

Mosquito currently supports following exchanges:
 * Poloniex - supporting *fillOrKill* and *immediateOrCancel* trading types. *postOnly* type is not supported. You can 
 read more about trading types [here.](https://github.com/s4w3d0ff/python-poloniex/blob/master/poloniex/__init__.py)


## Requirements
 * Python 3.*
 * mongodb



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
usage: backfill.py [-h] [--pair PAIR] [--all] --days DAYS

optional arguments:
  -h, --help   show this help message and exit
  --pair PAIR  Pair to backfill. For ex. [BTC_ETH]
  --all        Backfill data for ALL currencies
  --days DAYS  Number of days to backfill
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
 * **Paper** - mode simulating live ticker but placing fictive buy/sell orders.
 * **Live** - live trading with placing REAL buy/sell orders.

> Backtest and Paper trading are using immediate buy/sell orders by using the last ticker 
closing price. This results to NOT 100% accurate strategy results, what you should be aware of.
 

### Backtest
todo


### Paper
todo


### Live
todo



## Plot and Statistics
Mosquito has a simple plot utility for visualizing current pair combined with trading history. Visualization uses external library [plotly](https://plot.ly/).

[![mosquito_plot.png](https://s22.postimg.org/px5umpxr5/mosquito_plot.png)](https://postimg.org/image/3xzfzigwt/)



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
