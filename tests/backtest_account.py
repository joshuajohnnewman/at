import datetime
import unittest

from trading.backtest.account import Account
from trading.broker import MarketOrder
from trading.constants.order import SIDE_SELL, ORDER_MARKET
from trading.constants.instrument import INSTRUMENT_EUR_USD


class BacktestAccountTests(unittest.TestCase):
    def setUp(self):
        instrument = INSTRUMENT_EUR_USD
        base_pair = {'currency': 'usd', 'starting_units': 0}
        quote_pair = {'currency': 'eur', 'starting_units': 0}

        self.account = Account(instrument, base_pair, quote_pair)

    def test_representation(self):
        account_rep = str(self.account)

        self.assertEqual(account_rep, 'Instrument EUR_USD Profit 0 Base Pair: Currency: usd Starting Units: 0 '
                                      'Tradeable Units: 0 Quote Pair: Currency: eur Starting Units: 0 '
                                      'Tradeable Units: 0')

    def test_make_order(self):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"
        units = 1000
        price = 0.982

        instrument = self.account.instrument
        side = 'hold'
        order_type = ORDER_MARKET

        market_order = MarketOrder(instrument, units, side, order_type, price, trade_expire)

        with self.assertRaises(ValueError):
            self.account.make_order(market_order)

    def test_update_account_state(self):
        self.account.quote_pair.tradeable_units = 1000

        instrument = self.account.instrument
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"

        units = 1000
        price = 0.982
        order_type = ORDER_MARKET

        side = SIDE_SELL

        market_order = MarketOrder(instrument, units, side, order_type, price, trade_expire)

        self.assertEqual(self.account.profit, 0.0)
        self.account.make_order(market_order)

        trade_gain = units / price

        self.assertEqual(self.account.profit, trade_gain)
