import talib
from .base import Base


class Junior(Base):
    """
    Mid-size blueprint - EMA, RCI, CCI, OBV
    """

    def __init__(self, pairs):
        super(Junior, self).__init__('junior', pairs)
        self.min_history_ticks = 35

    @staticmethod
    def calculate_features(df):
        """
        Method which calculates and generates features
        """
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        last_row = df.tail(1).copy()

        periods = [2, 4, 8, 12, 16, 20]
        for period in periods:
            # ************** Calc EMAs
            ema = talib.EMA(close[-period:], timeperiod=period)[-1]
            last_row['ema' + str(period)] = ema

            # ************** Calc OBVs
            obv = talib.OBV(close[-period:], volume[-period:])[-1]
            last_row['obv' + str(period)] = obv

        # ************** Calc RSIs
        rsi_periods = [5]
        for rsi_period in rsi_periods:
            rsi = talib.RSI(close[-rsi_period:], timeperiod=rsi_period-1)[-1]
            last_row['rsi' + str(rsi_period)] = rsi
            last_row['rsi_above_50' + str(rsi_period)] = int(rsi > 50.0)

        # ************** Calc CCIs
        cci_periods = [5]
        for cci_period in cci_periods:
            cci = talib.CCI(high[-cci_period:],
                            low[-cci_period:],
                            close[-cci_period:],
                            timeperiod=cci_period)[-1]
            last_row['cci' + str(cci_period)] = cci

        # ************** Calc MACD 1
        macd_periods = [34]
        for macd_period in macd_periods:
            macd, macd_signal, _ = talib.MACD(close[-macd_period:],
                                              fastperiod=12,
                                              slowperiod=26,
                                              signalperiod=9)
            macd = macd[-1]
            signal_line = macd_signal[-1]
            last_row['macd_above_signal' + str(macd_period)] = int(macd > signal_line)
            last_row['macd_above_zero' + str(macd_period)] = int(macd > 0.0)

        return last_row
