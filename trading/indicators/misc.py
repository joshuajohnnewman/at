from trading.constants.interval import TRADING_PERIOD_MONTH
from trading.indicators.exceptions import TalibIntervalException
from trading.indicators.volatility_indicators import calc_average_true_range


def get_period_high(daily_highs, interval):
    """
    Gets high price of primary pair for target num days
    :param num_days: target num of days
    :returns: high price (float) over specified period
    """

    if len(daily_highs) < interval:
        raise TalibIntervalException

    target_range = daily_highs[-interval:]
    return max(target_range)


def get_period_low(daily_lows, interval):
    """
    Gets low price of primary pair for target num days
    :param num_days: target num of days
    :returns: low price (float) over specified period
    """
    if len(daily_lows) < interval:
        raise TalibIntervalException

    target_range = daily_lows[-interval:]
    return min(target_range)


def calc_chandalier_exits(close, high, low, volatility_threshold=3,
                          target_interval=TRADING_PERIOD_MONTH):
    """
    Volatility-based system that identifies outsized price movements
    Indicator provides a buffer that is three times the volatility
    A decline strong enough to break this level warrants a reevaluation of long positions
    """
    required_interval = target_interval + 1

    if len(close) < required_interval or len(high) < required_interval or len(close) < required_interval:
        raise TalibIntervalException

    close = close[-required_interval:]
    high = high[-required_interval:]
    low = low[-required_interval:]

    month_high = get_period_high(high, interval=required_interval)
    month_low = get_period_low(low, interval=required_interval)

    atr = calc_average_true_range(close, high, low, target_interval)  # original interval

    long_exit = month_high - (atr * volatility_threshold)
    short_exit = month_low + (atr * volatility_threshold)

    return long_exit, short_exit
