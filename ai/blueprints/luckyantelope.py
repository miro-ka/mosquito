import talib
from .base import Base


class Luckyantelope(Base):
    """
    Full blown blueprint - using 5m ticker
    """

    def __init__(self, pairs):
        super(Luckyantelope, self).__init__('luckyantelope', pairs)
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

        # ************** Calc EMAs
        ema_periods = [2, 4, 8, 12, 16, 20]
        for ema_period in ema_periods:
            ema = talib.EMA(close[-ema_period:], timeperiod=ema_period)[-1]
            last_row['ema' + str(ema_period)] = ema

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

        # ************** Calc OBVs
        obv_periods = [2, 4, 8, 12, 16, 20]
        for obv_period in obv_periods:
            obv = talib.OBV(close[-obv_period:], volume[-obv_period:])[-1]
            last_row['obv' + str(obv_period)] = obv

        return last_row


