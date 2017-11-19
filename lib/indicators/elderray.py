import talib


def elderray(close):
    """
    Elder ray Indicator (Bulls/Bears Power)
    Returns:
        0 - No condition met
        1 - Green Price Bar: (13-period EMA > previous 13-period EMA) and (MACD-Histogram > previous period's MACD-Histogram)
        2 - Red Price Bar:   (13-period EMA < previous 13-period EMA) and (MACD-Histogram < previous period's MACD-Histogram)

    Price bars are colored blue when conditions for a Red Price Bar or Green Price Bar are not met. The MACD-Histogram
    is based on MACD(12,26,9).
    """

    min_dataset_size = 36
    dataset_size = close.size
    if dataset_size < min_dataset_size:
        print('Error in elderray.py: passed not enough data! Required: ' + str(min_dataset_size) +
              ' passed: ' + str(dataset_size))
        return None

    # Calc EMA
    ema_period = 13
    ema = talib.EMA(close[-ema_period:], timeperiod=ema_period)[-1]
    ema_prev = talib.EMA(close[-ema_period-1:len(close)-1],
                         timeperiod=ema_period)[-1]

    # Calc MACD
    macd_period = 34
    macd, macd_signal, _ = talib.MACD(close[-macd_period:],
                                      fastperiod=12,
                                      slowperiod=26,
                                      signalperiod=9)
    macd = macd[-1:]

    macd_prev, macd_signal_prev, _ = talib.MACD(close[-macd_period-1:len(close)-1],
                                                fastperiod=12,
                                                slowperiod=26,
                                                signalperiod=9)
    macd_prev = macd_prev[-1:]

    # Green Price Bar
    if ema > ema_prev and macd > macd_prev:
        return 1

    # Red Price Bar
    if ema < ema_prev and macd < macd_prev:
        return 2

    return 0


