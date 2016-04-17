from collections import namedtuple

PrimaryPair = namedtuple('PrimaryPair', ('currency_a', 'currency_b'))

class Portfolio:

    def __init__(self, instrument, pair_a, pair_b):
        self.instrument = instrument
        self.pair_a = pair_a
        self.pair_b = pair_b
        print(pair_a)
        print(pair_b)
        self.primary_pair = PrimaryPair(pair_a['name'], pair_b['name'])
        self.profit = 0

    def __repr__(self):
        representation = 'Instrument {instrument} Profit {profit}'.format(instrument=self.instrument, profit=self.profit)
        return representation

    def update(self, order_response):
        pass



