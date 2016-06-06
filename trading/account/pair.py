from collections import namedtuple

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
