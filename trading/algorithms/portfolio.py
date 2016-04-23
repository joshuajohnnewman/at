from collections import namedtuple

PrimaryPair = namedtuple('PrimaryPair', ('currency_a', 'currency_b'))

class Portfolio:

    def __init__(self, instrument, pair_a, pair_b):
        pair_a['tradeable_currency'] = pair_a['amount']
        pair_a['initial_currency'] = pair_a['amount']
        pair_b['tradeable_currency'] = pair_b['amount']
        pair_b['initial_currency'] = pair_b['amount']
        self.instrument = instrument
        self.pair_a = pair_a
        self.pair_b = pair_b
        self.primary_pair = PrimaryPair(pair_a['name'], pair_b['name'])
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
        pass



