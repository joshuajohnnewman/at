import numpy as np
import talib

from trading.indicators.exceptions import TalibIntervalException


def calc_bollinger_bands():
    pass


def calc_double_exponential_moving_average():
    pass


def calc_exponential_moving_average():
    pass


def calc_hilbert_transformation():
    """
    Instantaneous trendline
    :return:
    """
    pass


def calc_kaufman_moving_average():
    pass


def calc_moving_average(data, interval):
    if len(data) < interval:
        raise TalibIntervalException

    data = data[:interval]

    target_data = np.asarray(data)
    return talib.MA(target_data, interval)[-1]


def calc_moving_average_variable_period():
    pass


def calc_midpoint_over_period():
    pass


def calc_midpoint_price_over_period():
    pass


def calc_parabolic_sar():
    pass


def calc_parabolic_sar_extended():
    pass


def calc_simple_moving_average():
    pass


def calc_triple_exponential_moving_average_t3():
    pass


def calc_triple_exponential_moving_average_tema():
    pass


def calc_triangular_moving_average():
    pass

