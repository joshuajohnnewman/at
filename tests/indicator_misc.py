import random
import unittest

from trading.indicators.misc import get_period_high, get_period_low, calc_chandalier_exits
from trading.indicators.exceptions import TalibIntervalException


class MiscIndicatorTests(unittest.TestCase):
    def test_get_period_low(self):
        one_hundred_data_points = range(0, 100)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        low = get_period_low(one_hundred_data_points, interval=len(one_hundred_data_points))
        self.assertEqual(low, 0.0)

        with self.assertRaises(TalibIntervalException):
            get_period_low(one_hundred_data_points, interval=200)

    def test_get_period_high(self):
        one_hundred_data_points = range(0, 100)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        high = get_period_high(one_hundred_data_points, interval=len(one_hundred_data_points))
        self.assertEqual(high, 99.0)

        with self.assertRaises(TalibIntervalException):
            get_period_high(one_hundred_data_points, interval=200)

    def test_calc_chandalier_exits(self):
        one_hundred_data_points = range(0, 100)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        low = [point - 5 for point in one_hundred_data_points]
        high = [point + 5 for point in one_hundred_data_points]
        close = [point + random.randint(-4, 4) for point in one_hundred_data_points]

        chandalier_exits = calc_chandalier_exits(close=close, high=high, low=low, target_interval=50)

        self.assertEqual(chandalier_exits, (74.0, 74.0))

        with self.assertRaises(TalibIntervalException):
            calc_chandalier_exits(close=close, high=high, low=low, target_interval=100)
