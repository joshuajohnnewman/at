import numpy as np
import talib

from trading.indicators.exceptions import TalibIntervalException


def calc_average_directional_movement_index(high, low, close, interval):
    """
    First data point is earliest
    :param high:
    :param low:
    :param close:
    :param interval:
    :return:
    """
    required_interval = interval * 2

    if len(high) < required_interval or len(low) < required_interval or len(close) < required_interval:
        raise TalibIntervalException

    high = high[-required_interval:]
    low = low[-required_interval:]
    close = close[-required_interval:]

    high = np.asarray(high)
    low = np.asarray(low)
    close = np.asarray(close)

    adx = talib.ADX(high, low, close, timeperiod=interval)
    return adx[-1]


def calc_average_directional_movement_index_rating(high, low, close, interval):
    """
    First data point is earliest
    :param high:
    :param low:
    :param close:
    :param interval:
    :return:
    """
    required_interval = interval * 3

    if len(high) < required_interval or len(low) < required_interval or len(close) < required_interval:
        raise TalibIntervalException

    high = high[-required_interval:]
    low = low[-required_interval:]
    close = close[-required_interval:]

    high = np.asarray(high)
    low = np.asarray(low)
    close = np.asarray(close)
    adxr = talib.ADXR(high, low, close, timeperiod=interval)

    return adxr[-1]


def calc_absolute_price_oscillator():
    pass


def calc_aroon():
    pass


def calc_aroon_oscillator():
    pass


def calc_balance_of_power():
    pass


def calc_commodity_channel_index():
    pass


def calc_chande_momentum_oscillator():
    pass


def calc_directional_movement_index():
    pass


def calc_moving_average_convergence_divergence():
    pass


def calc_macd_with_controllable_ma_type():
    pass


def calc_money_flow_index():
    pass


def calc_minus_directional_indicator():
    pass


def calc_minus_directional_movement():
    pass


def calc_momentum():
    pass


def calc_plus_directional_indicator():
    pass


def calc_plus_directional_movement():
    pass


def calc_percetntage_price_oscillator():
    pass


def calc_rate_of_change():
    pass


def calc_rate_of_change_percentage():
    pass


def calc_rate_of_change_ration():
    pass


def calc_rate_of_change_ratio():
    pass


def calc_rate_of_change_100_scale():
    pass


def calc_relative_strength_index():
    pass


def calc_schotastic():
    pass


def calc_schotastic_fast():
    pass


def calc_schotastic_relative_strength_index():
    pass


def calc_one_day_rate_of_change_of_a_tripple_smooth_ema():
    pass


def calc_ultimate_oscillator():
    pass


def calc_williams_percent_r():
    pass




