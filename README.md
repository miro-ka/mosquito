# evobot
Evolutionary Trading Bot coded in Python 3, inspired by [zenbot](https://github.com/carlos8f/zenbot)


## About


## Requirements
 * Python 3.*
 * mongodb


## Quick Start



### Install
 1. clone repo
 ```
 git clone https://github.com/miti0/evobot.git
 ```
 2. install mongodb & required python packages
 
 3. set-up config.ini (if you want to use sample config, just rename config.sample.ini to config.ini)
 
 3. Run desired command (full list of commands below)
 
 

### Backfill
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



### License: MIT

- Copyright (C) 2017 Miroslav Karpis (miti0)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the &quot;Software&quot;), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED &quot;AS IS&quot;, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.