from abc import abstractmethod, ABCMeta
from collections import namedtuple
from decimal import Decimal

from trading.algorithms.constants import INTERVAL_ONE_HOUR
from trading.util.log import Logger

PrimaryPair = namedtuple('PrimaryPair', ('currency_a', 'currency_b'))


class Strategy():
    __metaclass__ = ABCMeta

    interval = INTERVAL_ONE_HOUR

    _name = 'Base Strategy'
    _portfolio = {
        'instrument': None,
        'primary_pair': (),
        'pair_a': {'name': '', 'tradeable_currency': ''},
        'pair_b': {'name': '', 'tradeable_currency': ''}
    }

    def __init__(self, primary_pair, starting_currency, instrument):
        self.set_instrument(instrument)
        self.set_primary_pair(primary_pair['a'], primary_pair['b'])
        self.set_starting_currencies(starting_currency['a'], starting_currency['b'])
        self.log_strategy_parms()

    def log_strategy_parms(self):
        message = 'Initialied Strategy {name} at interval of {interval} with instrument of {instrument} ' \
                  'primary pair {primary_pair} with pair_a {pair_a} and pair_b {pair_b}'\
            .format(name=self._name, interval=self.interval, instrument=self._portfolio['instrument'],
                    pair_a=self._portfolio['pair_a'], pair_b=self._portfolio['pair_b'])
        self.logger.info(message=message)


    def set_instrument(self, instrument):
        self._portfolio['instrument'] = instrument

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