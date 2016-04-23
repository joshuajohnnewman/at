import time

from abc import abstractmethod, ABCMeta
from bson import ObjectId

from trading.algorithms.constants import INTERVAL_ONE_HOUR
from trading.algorithms.portfolio import Portfolio
from trading.db import get_database
from trading.indicators import INTERVAL_FORTY_DAYS
from trading.util.log import Logger


class Strategy(object):
    __metaclass__ = ABCMeta

    _db = None
    _logger = None

    interval = INTERVAL_ONE_HOUR
    strategy_data = {}

    name = 'Base Strategy'

    def __init__(self, config):
        instrument = config['instrument']
        pair_a = config['pair_a']
        pair_b = config['pair_b']

        self.portfolio = Portfolio(instrument, pair_a, pair_b)
        self.instrument = instrument
        self.logger.info('Starting Portfolio', data=self.portfolio)
        self.data_window = INTERVAL_FORTY_DAYS

    @abstractmethod
    def analyze_data(self, market_data):
        raise NotImplementedError

    @abstractmethod
    def make_decision(self):
        raise NotImplementedError

    @abstractmethod
    def calc_amount_to_buy(self, current_price):
        raise NotImplementedError

    @abstractmethod
    def calc_amount_to_sell(self, current_price):
        raise NotImplementedError

    @abstractmethod
    def allocate_tradeable_amount(self):
        raise NotImplementedError

    @abstractmethod
    def make_order(self, current_price):
        raise NotImplementedError

    def shutdown_strategy(self, started_at, ended_at, num_ticks, shutdown_cause):
        self.logger.info('Shutdown Strategy')

    def update_portfolio(self, order_response):
        self.portfolio.update(order_response)

    def log_strategy_data(self):
        self.logger.info('Strategy Data', data=self.strategy_data)

    def load_strategy(self, strategy_id):
        query = {'_id': ObjectId(strategy_id)}
        strategy = self.db.strategies.find_one(query)
        strategy_data = strategy['strategy_data']
        config = strategy_data['config']
        return config

    @staticmethod
    def make_trading_session_info(started_at, ended_at, num_ticks, shutdown_cause):
        return {
            'session_id': time.time(),
            'started_at': started_at,
            'ended_at': ended_at,
            'num_ticks': num_ticks,
            'shutdown_cause': shutdown_cause
        }

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db