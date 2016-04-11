import numpy
import talib

def calc_std(data, interval):
    target_data = numpy.asarray(data[interval:])
    talib.std(target_data)
