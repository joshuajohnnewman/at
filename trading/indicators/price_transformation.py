import numpy as np
import talib


def calc_average_price():
    pass


def calc_median_price():
    pass


def calc_typical_price():
    pass


def calc_weighted_close_price():
    pass


def calc_standard_deviation(data, interval):
    data = np.asarray(data)
    stdev = talib.STDDEV(data, timeperiod=len(data))
    return stdev[-1]