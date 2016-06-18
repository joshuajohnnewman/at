import time
from abc import abstractmethod, ABCMeta

from bson import ObjectId

from trading.account.portfolio import Portfolio
from trading.broker.constants import GRANULARITY_HOUR
from trading.db import get_database
from trading.indicators import INTERVAL_FORTY_CANDLES
from trading.util.log import Logger


class Strategy(object):
    __metaclass__ = ABCMeta

    _db = None
    _logger = None

    interval = 600
    strategy_data = {}
    data_window = INTERVAL_FORTY_CANDLES
    granularity = GRANULARITY_HOUR

    name = 'Base Strategy'

    def __init__(self, strategy_config):
        instrument = strategy_config['instrument']
        base_pair = strategy_config['base_pair']
        quote_pair = strategy_config['quote_pair']

        self.instrument = instrument
        self.portfolio = Portfolio(instrument, base_pair, quote_pair)

        self.logger.info('Starting Portfolio', data=self.portfolio)

    @abstractmethod
    def analyze_data(self, market_data):
        raise NotImplementedError

    @abstractmethod
    def make_decision(self):
        raise NotImplementedError

    @abstractmethod
    def calc_units_to_buy(self, current_price):
        raise NotImplementedError

    @abstractmethod
    def calc_units_to_sell(self, current_price):
        raise NotImplementedError

    @abstractmethod
    def allocate_tradeable_amount(self):
        raise NotImplementedError

    @abstractmethod
    def make_order(self, current_price):
        raise NotImplementedError

    def shutdown(self, started_at, ended_at, num_ticks, num_orders, shutdown_cause):
        self.logger.info('Shutdown Strategy')

    def update_portfolio(self, order_responses):
        self.portfolio.update(order_responses)

    def log_strategy_data(self):
        self.logger.debug('Strategy Indicator Data:')
        for indicator in self.strategy_data:
            self.logger.debug('Indicator {indicator} with value {value}'
                             .format(indicator=indicator, value=self.strategy_data[indicator]))

    def load_strategy(self, strategy_id):
        query = {'_id': ObjectId(strategy_id)}
        strategy = self.db.strategies.find_one(query)
        strategy_data = strategy['strategy_data']
        config = strategy_data['config']
        return config

    def make_trading_session_info(self, started_at, ended_at, num_ticks, num_orders, shutdown_cause):
        return {
            'profit': self.portfolio.profit,
            'session_id': time.time(),
            'started_at': started_at,
            'ended_at': ended_at,
            'num_ticks': num_ticks,
            'num_orders': num_orders,
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