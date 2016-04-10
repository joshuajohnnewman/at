from trading.algorithms.base import Strategy
from trading.algorithms.constants import SELL_ALL


class Josh(Strategy):

    _tradeable_currency = None

    def __init__(self, primary_pair, ):
        super(Josh).__init__(primary_pair)

    def calc_amount_to_buy(self, current_price):
        target_amount = self.tradeable_currency_a / current_price
        self.logger.log('Target_btc', data=target_amount)
        return target_amount

    def calc_amount_to_sell(self):
        return SELL_ALL

    def allocate_tradeable_amount(self):
        profit = portfolio.eur - storage.starting_currency
        if profit > 0:
            storage.tradeable_currency = storage.starting_currency
            storage.profit = profit
        else:
            storage.tradeable_currency = portfolio.eur
        log('Allocation {alloc}'.format(alloc=storage.tradeable_currency))

    def make_decision(self, data):
        pass

    def analyze_data(self, data):
        pass