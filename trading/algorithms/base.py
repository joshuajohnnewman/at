from abc import abstractmethod, ABCMeta
from collections import namedtuple
from decimal import Decimal

from trading.util.log import Logger

PrimaryPair = namedtuple('PrimaryPair', ('currency_a', 'currency_b'))

class Strategy():
    __metaclass__ = ABCMeta

    _portfolio = {
        'primary_pair': (),
        'pair_a': {'name': '', 'tradeable_currency': ''},
        'pair_b': {'name': '', 'tradeable_currency': ''}
    }

    def __init__(self, primary_pair, starting_currency):
        self.set_primary_pair(primary_pair['a'], primary_pair['b'])
        self.set_starting_currencies(starting_currency['a'], starting_currency['b'])

    def passes_filter(self, datum):
        return True

    def set_primary_pair(self, currency_a, currency_b):
        self.portfolio. primary_pair = PrimaryPair(currency_a, currency_b)

    def set_tradeable_currency(self, currency_a, currency_b):
        currency_a = self._portfolio['pair_a']
        currency_b = self._portfolio['pair_b']
        currency_a['name'] = currency_a['name']
        currency_a['tradeable_currency'] = Decimal(currency_a['amount'])

        currency_b['name'] = currency_b['name']
        currency_b['tradeable_currency'] = Decimal(currency_b['amount'])

    @abstractmethod
    def calc_amount_to_buy(self):
        return NotImplementedError

    @abstractmethod
    def calc_amount_to_sell(self):
        return NotImplementedError

    @abstractmethod
    def allocate_tradeable_amount(self):
        return NotImplementedError

    @abstractmethod
    def make_decision(self, data):
        return NotImplementedError

    @abstractmethod
    def analyze_data(self, data):
        return NotImplementedError

    @abstractmethod
    def update_portfolio(self, data):
        return NotImplementedError

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger