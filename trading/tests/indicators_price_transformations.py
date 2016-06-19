import unittest

from trading.indicators.exceptions import TalibIntervalException
from trading.indicators.price_transformation import calc_standard_deviation


class PriceTransformationTests(unittest.TestCase):
    def test_standard_deviation(self):
        one_hundred_data_points = range(0, 100)
        one_hundred_data_points = [float(val) for val in one_hundred_data_points]

        sd = calc_standard_deviation(one_hundred_data_points, interval=100)
        self.assertEqual(sd, 28.866070047722118)

        sd = calc_standard_deviation(one_hundred_data_points, interval=30)
        self.assertEqual(sd, 8.6554414483992073)

        with self.assertRaises(TalibIntervalException):
            self.assertRaises(calc_standard_deviation(one_hundred_data_points, interval=2000))
