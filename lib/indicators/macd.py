import talib
import math


def macd(close, previous_macds=[], fast_period=12, slow_period=26, signal_period=9):
    """
    MACD - Moving Average Convergence Divergence
    previous_macd: numpy.ndarray of previous MACDs
    Returns:
        - macd
        - macd_line
    """
    ema_slow = talib.EMA(close, timeperiod=slow_period)[-1]
    ema_fast = talib.EMA(close[-fast_period:], timeperiod=fast_period)[-1]

    macd_value = ema_fast - ema_slow
    # if math.isnan(macd_value):
    #    print('Macd got nan:', close)

    # print('previous_macds:', previous_macds)
    if len(previous_macds) < signal_period:
        signal_line = None
    else:
        signal_line = talib.EMA(previous_macds[-signal_period:], timeperiod=signal_period)[-1]

    return macd_value, signal_line



