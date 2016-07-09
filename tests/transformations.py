import unittest

from trading.constants.price_data import PRICE_ASK, PRICE_ASK_CLOSE, PRICE_ASK_HIGH
from trading.util.transformations import get_last_candle_data, normalize_current_price_data, normalize_price_data


class PriceDataTransformationTests(unittest.TestCase):
    def setUp(self):
        self.candle_data = [
            {
                u'highAsk': 1.11271,
                u'lowAsk': 1.11173,
                u'complete': True,
                u'openBid': 1.1122,
                u'closeAsk': 1.11195,
                u'closeBid': 1.11177,
                u'volume': 438,
                u'openAsk': 1.11239,
                u'time': u'2016-06-24T19:20:00.000000Z',
                u'lowBid': 1.11146,
                u'highBid': 1.11247
            },
            {
                u'highAsk': 1.11226,
                u'lowAsk': 1.11089,
                u'complete': True,
                u'openBid': 1.11183,
                u'closeAsk': 1.11197,
                u'closeBid': 1.11174,
                u'volume': 594,
                u'openAsk': 1.11197,
                u'time': u'2016-06-24T19:30:00.000000Z',
                u'lowBid': 1.11068,
                u'highBid': 1.112
            }
        ]

    def test_get_last_candle_data(self):
        last_candle = get_last_candle_data(self.candle_data)

        self.assertEqual(last_candle, {
                u'highAsk': 1.11226,
                u'lowAsk': 1.11089,
                u'complete': True,
                u'openBid': 1.11183,
                u'closeAsk': 1.11197,
                u'closeBid': 1.11174,
                u'volume': 594,
                u'openAsk': 1.11197,
                u'time': u'2016-06-24T19:30:00.000000Z',
                u'lowBid': 1.11068,
                u'highBid': 1.112
            })

    def test_normalize_current_price_data(self):
        current_price_data = {u'prices': [{u'ask': 1.09953, u'instrument': u'EUR_USD', u'bid': 1.09935,
                                           u'time': u'2016-06-27T01:50:37.839417Z'}]}

        asking_price = normalize_current_price_data(current_price_data, target_field=PRICE_ASK)

        self.assertEqual(asking_price, 1.09953)

    def test_normalize_price_data(self):
        high_price_data = normalize_price_data(self.candle_data, target_field=PRICE_ASK_HIGH)

        self.assertEqual(high_price_data, [1.11271, 1.11226])

        close_price_data = normalize_price_data(self.candle_data, target_field=PRICE_ASK_CLOSE)

        self.assertEqual(close_price_data, [1.11195, 1.11197])

