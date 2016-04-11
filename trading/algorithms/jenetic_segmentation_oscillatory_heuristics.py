from trading.algorithms.base import Strategy
from trading.algorithms.constants import SELL_ALL


class Josh(Strategy):

    _tradeable_currency = None

    def __init__(self, primary_pair, ):
        super(Josh).__init__(primary_pair)

    def calc_amount_to_buy(self):
        pass

    def calc_amount_to_sell(self):
        pass

    def allocate_tradeable_amount(self):
        pass

    def make_decision(self, data):
        pass

    def analyze_data(self, data):
        pass