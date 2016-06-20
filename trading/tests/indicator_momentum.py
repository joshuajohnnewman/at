import random
import unittest

from trading.indicators.exceptions import TalibIntervalException
from trading.indicators.momentum_indicators import calc_average_directional_movement_index, calc_average_directional_movement_index_rating


class MomentumIndicatorTests(unittest.TestCase):
    def test_average_directional_movement_index(self):
        one_hundred_data_points = range(50, 150)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        low = [point - 5 for point in one_hundred_data_points]
        high = [point + 5 for point in one_hundred_data_points]
        close = [point + random.randint(-4, 4) for point in one_hundred_data_points]

        adx = calc_average_directional_movement_index(high=high, low=low, close=close, interval=5)
        self.assertEqual(adx, 100)

        with self.assertRaises(TalibIntervalException):
            calc_average_directional_movement_index_rating(high=high, low=low, close=close, interval=200)

    def test_average_directional_movement_rating(self):
        one_hundred_data_points = range(0, 100)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        low = [point - 5 for point in one_hundred_data_points]
        high = [point + 5 for point in one_hundred_data_points]
        close = [point + random.randint(-4, 4) for point in one_hundred_data_points]

        adxr = calc_average_directional_movement_index_rating(high=high, low=low, close=close, interval=5)
        self.assertEqual(adxr, 100)

        with self.assertRaises(TalibIntervalException):
            calc_average_directional_movement_index_rating(high=high, low=low, close=close, interval=200)
