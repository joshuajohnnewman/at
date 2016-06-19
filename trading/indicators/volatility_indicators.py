import numpy as np
import talib

from trading.indicators.exceptions import TalibIntervalException


def calc_average_true_range(close, high, low, interval):
    if len(high) < interval or len(low) < interval or len(close) < interval:
        raise TalibIntervalException

    high = high[-interval:]
    low = low[-interval:]
    close = close[-interval:]

    high = np.asarray(high)
    low = np.asarray(low)
    close = np.asarray(close)
    atr = talib.ATR(high, low, close, timeperiod=interval)
    return atr[-1]


def calc_normalized_average_true_range():
    pass


def calc_true_range():
    pass
