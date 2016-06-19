import unittest

from trading.indicators.overlap_studies import calc_moving_average
from trading.indicators.exceptions import TalibIntervalException


class OverLapStudiesTests(unittest.TestCase):
    def test_moving_average(self):
        one_hundred_data_points = range(0, 100)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        ma = calc_moving_average(one_hundred_data_points, interval=len(one_hundred_data_points))

        self.assertEqual(ma, 98.5)

        ma = calc_moving_average(one_hundred_data_points, interval=50)

        self.assertEqual(ma, 98.5)

        with self.assertRaises(TalibIntervalException):
            calc_moving_average(one_hundred_data_points, interval=200)
