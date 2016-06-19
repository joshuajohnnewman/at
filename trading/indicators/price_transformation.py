import numpy as np
import talib

from trading.indicators.exceptions import TalibIntervalException


def calc_average_price():
    pass


def calc_median_price():
    pass


def calc_typical_price():
    pass


def calc_weighted_close_price():
    pass


def calc_standard_deviation(data, interval):
    if len(data) < interval:
        raise TalibIntervalException

    data = data[-interval:]
    data = np.asarray(data)
    stdev = talib.STDDEV(data, timeperiod=interval)
    return stdev[-1]