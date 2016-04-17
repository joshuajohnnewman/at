import numpy
import talib

def calc_atr(close, high, low, interval):
    # Todo fix range logic
    high = numpy.asarray(high)
    low = numpy.asarray(low)
    close = numpy.asarray(close)
    atr = talib.ATR(high, low, close, timeperiod=interval)
    return atr[-1]
