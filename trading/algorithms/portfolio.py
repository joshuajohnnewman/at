from collections import namedtuple
from trading.broker import SIDE_SELL, SIDE_BUY
from trading.util.log import Logger

PrimaryPair = namedtuple('PrimaryPair', ('base', 'quote'))


class Pair:
    def __init__(self, currency, starting_units, tradeable_units):
        self.currency = currency
        self.starting_units = starting_units
        self.tradeable_units = tradeable_units

    def __repr__(self):
        representation = 'Currency: {currency} Starting Units: {start_units} Tradeable Units: {trade_units}' \
            .format(currency=self.currency, start_units=self.starting_units, trade_units=self.tradeable_units)
        return representation


class Portfolio:

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

    def serialize(self):
        return {
            'profit': self.profit,
            'base_pair': self.base_pair,
            'quote_pair': self.quote_pair,
            'instrument': self.instrument
        }

    def update(self, order_responses):
        for order_id in order_responses:
            order_response = order_responses[order_id]

            self.logger.info('Updating Portfolio from order response {response}'.format(response=order_response))

            order = order_response['tradeOpened']
            units = order['units']
            side = order['side']
            price = order_response['price']

            total_traded = units * price

            if side == SIDE_SELL:
                current_base_units = self.base_pair.tradeable_units
                current_quote_units = self.quote_pair.tradeable_units
                self.quote_pair_tradeable_units = current_quote_units - total_traded
                self.base_pair.tradeable_units = current_base_units + total_traded

            elif side == SIDE_BUY:
                current_base_units = self.base_pair.tradeable_units
                current_quote_units = self.quote_pair.tradeable_units
                self.base_pair.tradeable_units = current_base_units - total_traded
                self.quote_pair.tradeable_units = current_quote_units + total_traded

        self.profit = self.base_pair.tradeable_units - self.base_pair.starting_units

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger
