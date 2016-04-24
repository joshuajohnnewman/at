import numpy as np
import talib


def calc_average_true_range(close, high, low, interval):
    high = np.asarray(high)
    low = np.asarray(low)
    close = np.asarray(close)
    atr = talib.ATR(high, low, close, timeperiod=interval)
    return atr[-1]


def calc_normalized_average_true_range():
    pass


def calc_true_range():
    pass
