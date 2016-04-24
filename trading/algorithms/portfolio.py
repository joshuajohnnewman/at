from collections import namedtuple
from trading.broker import SIDE_SELL, SIDE_BUY

PrimaryPair = namedtuple('PrimaryPair', ('currency_a', 'currency_b'))

class Portfolio:

    def __init__(self, instrument, pair_a, pair_b):
        pair_a['tradeable_currency'] = pair_a['amount']
        pair_a['initial_currency'] = pair_a['amount']
        pair_b['tradeable_currency'] = pair_b['amount']
        pair_b['initial_currency'] = pair_b['amount']
        self.pair_a = pair_a
        self.pair_b = pair_b
        self.primary_pair = PrimaryPair(pair_a['name'], pair_b['name'])

        self.instrument = instrument
        self.profit = 0

    def __repr__(self):
        representation = 'Instrument {instrument} Profit {profit} Pair A: {pa} Pair B: {pb}'\
            .format(instrument=self.instrument, profit=self.profit, pa=self.pair_a, pb=self.pair_b)
        return representation

    def serialize(self):
        return {
            'profit': self.profit,
            'pair_a': self.pair_a,
            'pair_b': self.pair_b,
            'instrument': self.instrument
        }

    def update(self, order_response):
        order = order_response['orderOpened']
        units = order['units']
        side = order['side']
        price = order_response['price']

        total_traded = units * price

        if side == SIDE_SELL:
            current_pair_a = self.pair_a['tradeable_currency']
            current_pair_b = self.pair_b['tradeable_currency']
            new_pair_b = current_pair_b - total_traded
            new_pair_a = current_pair_a + total_traded
            self.pair_a['tradeable_currency'] = new_pair_a
            self.pair_b['tradeable_currency'] = new_pair_b
        elif side == SIDE_BUY:
            current_pair_a = self.pair_a['tradeable_currnecy']
            current_pair_b = self.pair_b['tradeable_currency']
            new_pair_a = current_pair_a - total_traded
            new_pair_b = current_pair_b + total_traded
            self.pair_a['tradeable_currency'] = new_pair_a
            self.pair_b['tradeable_currency'] = new_pair_b

        self.profit = self.pair_a['initial_currency'] - self.pair_a['tradeable_currency']
