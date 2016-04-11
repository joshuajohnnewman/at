import numpy
import talib


def calc_ma(data, interval):
    target_data = numpy.asarray(data)
    return talib.ma(target_data, interval)