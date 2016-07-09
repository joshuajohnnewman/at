import random
import unittest

from trading.indicators.volatility_indicators import calc_average_true_range
from trading.indicators.exceptions import TalibIntervalException


class MiscIndicatorTests(unittest.TestCase):
    def test_calculate_average_true_range(self):
        one_hundred_data_points = range(0, 100)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        low = [point - 5 for point in one_hundred_data_points]
        high = [point + 5 for point in one_hundred_data_points]
        close = [point + random.randint(-4, 4) for point in one_hundred_data_points]

        atr = calc_average_true_range(high=high, low=low, close=close, interval=50)

        self.assertEqual(atr, 10.0)

        with self.assertRaises(TalibIntervalException):
            calc_average_true_range(high=high, low=low, close=close, interval=100)
