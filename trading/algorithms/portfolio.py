from collections import namedtuple
from trading.broker import SIDE_SELL, SIDE_BUY

PrimaryPair = namedtuple('PrimaryPair', ('a', 'b'))
Pair = namedtuple('Pair', ('name', 'starting_currency', 'tradeable_currency'))

class Portfolio:

    def __init__(self, instrument, pair_a, pair_b):
        self.pair_a = Pair(pair_a['name'], pair_a['starting_currency'], pair_a['tradeable_currency'])
        self.pair_b = Pair(pair_b['name'], pair_b['starting_currency'], pair_b['tradeable_currency'])
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
        print(order_response)
        order = order_response['tradeOpened']
        units = order['units']
        side = order['side']
        price = order_response['price']

        total_traded = units * price

        if side == SIDE_SELL:
            current_pair_a = self.pair_a.tradeable_currency
            current_pair_b = self.pair_b.tradeable_currency
            new_pair_b_tradeable = current_pair_b - total_traded
            new_pair_a_tradeable = current_pair_a + total_traded
            self.pair_a.tradeable_currency = new_pair_a_tradeable
            self.pair_b.tradeable_currency = new_pair_b_tradeable
        elif side == SIDE_BUY:
            current_pair_a = self.pair_a.tradeable_currency
            current_pair_b = self.pair_b.tradeable_currency
            new_pair_a_tradeable = current_pair_a - total_traded
            new_pair_b_tradeable = current_pair_b + total_traded
            self.pair_a.tradeable_currency = new_pair_a_tradeable
            self.pair_b.tradeable_currency = new_pair_b_tradeable

        self.profit = self.pair_a.starting_currency - self.pair_a.tradeable_currency
