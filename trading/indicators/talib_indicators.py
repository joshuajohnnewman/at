import numpy
import talib


def calc_std(data, interval):
    data = numpy.asarray(data)
    stdev = talib.STDDEV(data, timeperiod=len(data))
    return stdev[-1]


def calc_ma(data, interval):
    target_data = numpy.asarray(data)
    return talib.MA(target_data, interval)[-1]


def calc_atr(close, high, low, interval):
    # Todo fix range logic
    high = numpy.asarray(high)
    low = numpy.asarray(low)
    close = numpy.asarray(close)
    atr = talib.ATR(high, low, close, timeperiod=interval)
    return atr[-1]
