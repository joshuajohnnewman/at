import datetime
import unittest

from trading.backtest.backtest_data_broker import BacktestDataBroker
from trading.broker import MarketOrder
from trading.constants.order import SIDE_SELL, ORDER_MARKET
from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.constants.granularity import GRANULARITY_DAY
from trading.backtest.exceptions import BacktestBrokerException


class BacktestDataBrokerTests(unittest.TestCase):
    def setUp(self):
        count = 20
        granularity = GRANULARITY_DAY
        instrument = INSTRUMENT_EUR_USD
        base_pair = {'currency': 'usd', 'starting_units': 0}
        quote_pair = {'currency': 'eur', 'starting_units': 0}

        data_file = '/Users/jnewman/Projects/automated_trading/data/M10_2001.json'
        self.broker = BacktestDataBroker(instrument, base_pair, quote_pair, data_file)
        self.broker.get_backtest_price_data(count, granularity)

    def test_get_account_information(self):
        account_id = self.broker.account_id
        account_info = self.broker.get_account_info()

        self.assertEqual(account_info['accountId'], account_id)
        self.assertEqual(account_info['openOrders'], 0)
        self.assertEqual(account_info['openTrades'], 0)
        self.assertEqual(account_info['balance'], 0)
        self.assertEqual(account_info['accountCurrency'], 'usd')

    def test_get_current_price_data(self):
        with self.assertRaises(IndexError):
            self.broker.get_current_price_data(tick=100000)

        first_candle = self.broker.get_current_price_data(tick=0)
        first_time = first_candle['prices'][0]['time']

        self.assertEqual(first_candle, {'prices': [{'ask': 0.947, 'instrument': 'EUR_USD', 'time': u'04:17'}]})

        second_candle = self.broker.get_current_price_data(tick=1)

        self.assertEqual(second_candle,  {'prices': [{'ask': 0.9469, 'instrument': 'EUR_USD', 'time': u'04:18'}]})

        second_time = second_candle['prices'][0]['time']

        self.assertEqual(first_time, '04:17')
        self.assertEqual(second_time, '04:18')

        tenth_candle = self.broker.get_current_price_data(tick=10)

        self.assertEqual(tenth_candle['prices'][0]['time'], '04:27')

    def test_get_historical_price_data(self):
        count = 2000000
        granularity = GRANULARITY_DAY

        with self.assertRaises(BacktestBrokerException):
            self.broker.get_historical_price_data(count, granularity)

        count = 20

        historical_price_data = self.broker.get_historical_price_data(count, granularity, tick=0)

        self.assertEqual(len(historical_price_data['candles']), count)

        g = historical_price_data['granularity']
        i = historical_price_data['instrument']
        candles = historical_price_data['candles']

        self.assertEqual(i, self.broker.instrument)
        self.assertEqual(g, granularity)
        self.assertEqual(candles[0], {u'highAsk': 0.947, u'lowAsk': 0.947, u'closeAsk': 0.947, u'volume': u'0',
                                      u'openAsk': 0.947, u'time': u'04:17', u'date': u'2001.01.02'})

    def test_get_order(self):
        order_id = 2
        order = self.broker.get_order(order_id)

        self.assertEqual(order, {})

    def test_make_order(self):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"
        units = 1000
        price = 0.982

        instrument = self.broker.instrument
        side = SIDE_SELL
        order_type = ORDER_MARKET

        market_order = MarketOrder(instrument, units, side, order_type, price, trade_expire)

        order_confirmation = self.broker.make_order(market_order)

        price = order_confirmation['price']
        instrument = order_confirmation['instrument']
        trades_closed = order_confirmation['tradesClosed']
        first_trade = trades_closed[0]
        units = first_trade['units']

        self.assertEqual(units, 1000)
        self.assertEqual(price, 0.982)
        self.assertEqual(instrument, INSTRUMENT_EUR_USD)

