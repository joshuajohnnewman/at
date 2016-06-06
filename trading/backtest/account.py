from trading.account.pair import Pair, PrimaryPair
from trading.broker import SIDE_BUY, SIDE_SELL

from trading.util.log import Logger

class Account:

    _logger = None

    def __init__(self, instrument, base_pair, quote_pair):
        self.base_pair = Pair(base_pair['currency'], base_pair['starting_units'], base_pair['tradeable_units'])
        self.quote_pair = Pair(quote_pair['currency'], 0, 0)
        self.primary_pair = PrimaryPair(base_pair['currency'], quote_pair['currency'])

        self.instrument = instrument
        self.profit = 0

    def __repr__(self):
        representation = 'Instrument {instrument} Profit {profit} Base Pair: {pa} Quote Pair: {pb}'\
            .format(instrument=self.instrument, profit=self.profit, pa=self.base_pair, pb=self.quote_pair)
        return representation

    def make_order(self, order):
        instrument = order.instrument
        units = order.units
        side = order.side
        type = order.type
        price = order.price
        expiry = order.expiry

        if side == SIDE_BUY:
            traded_units = units * price
            self.quote_pair['tradeable_units'] -= traded_units
            self.base_pair['tradeable_units'] += units

        elif side == SIDE_SELL:
            traded_units = units * price

            self.quote_pair['tradeable_units'] -= units
            self.base_pair['tradeable_units'] += traded_units

        else:
            # Todo: make backtest exceptions
            raise ValueError()

        self.update_account_state(price)

    def update_account_state(self, current_price):
        hypothetical_profit_total = (current_price * self.quote_pair.tradeable_units) + self.base_pair.tradeable_units
        self.profit = hypothetical_profit_total

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger
