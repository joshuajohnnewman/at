import datetime
import time

from abc import abstractmethod, ABCMeta

from trading.algorithms import initialize_strategy
from trading.constants.order import SIDE_SELL, SIDE_BUY, SIDE_STAY
from trading.constants.price_data import PRICE_ASK
from trading.db import get_database
from trading.live.exceptions import LiveTradingException, StrategyException
from trading.live.util import MAP_ORDER_TYPES, normalize_portfolio_update
from trading.util.log import Logger
from trading.util.transformations import normalize_current_price_data


class TradingStrategyRunner(object):
    __metaclass__ = ABCMeta

    _db = None
    _logger = None

    orders = {}
    invested = False
    tick_num = 0

    def __init__(self, broker, instrument, strategy_name, base_pair, quote_pair, strategy_id, classifier_id):
        self.num_orders = 0
        self.start_time = time.time()

        self.broker = broker
        account_information = self.broker.get_account_information()

        self.strategy = initialize_strategy(account_information, instrument, strategy_name, base_pair, quote_pair,
                                            strategy_id, classifier_id)
        self.interval = self.strategy.interval
        self.instrument = self.strategy.instrument

    @abstractmethod
    def tick(self):
        raise NotImplementedError

    def get_order_updates(self):
        order_ids = self.orders.keys()
        order_info_map = {}

        for order_id in order_ids:
            order_information = self.broker.get_order(order_id)
            order_info_map[order_id] = order_information

        return order_info_map

    def update_strategy_portfolio(self, order_responses):
        if order_responses:
            self.strategy.update_portfolio(order_responses)
            order_ids = order_responses.keys()
            self.remove_recorded_orders(order_ids)

    def remove_recorded_orders(self, order_responses):
        order_ids = order_responses.keys()

        for order_id in order_ids:
            del self.orders[order_id]

    def shutdown(self, shutdown_cause):
        shutdown_cause = str(shutdown_cause)
        end_time = time.time()

        if self.invested:
            self.logger.info('Invested, Not Closing out position')

        serialized_strategy = self.strategy.serialize()
        strategy_id = self.strategy.strategy_id
        session = self.make_trading_session_info(self.start_time, end_time, self.tick_num, self.num_orders,
                                                 shutdown_cause)

        query = {'_id': strategy_id}
        update = {'$set': {'strategy_data': serialized_strategy}, '$push': {'sessions': session}}
        self.db.strategies.update(query, update, upsert=True)

    def make_trading_session_info(self, started_at, ended_at, num_ticks, num_orders, shutdown_cause):
        return {
            'profit': self.strategy.portfolio.profit,
            'session_id': time.time(),
            'started_at': started_at,
            'ended_at': ended_at,
            'num_ticks': num_ticks,
            'num_orders': num_orders,
            'shutdown_cause': shutdown_cause
        }

    def log_market_order(self, decision, market_order):
        now = datetime.datetime.now()

        order_type = market_order.type
        num_units = market_order.units
        instrument = market_order.instrument
        price = market_order.price
        expiry = market_order.expiry
        strategy_name = self.strategy.name

        self.logger.info('Making {decision} market order at time {now}'.format(decision=decision, now=now))
        self.logger.info('{order_type} order of {num_units} units of instrument {instrument} at price {price} with '
                         'expiry at {expiry} for strategy {strategy_name}'
                         .format(order_type=order_type, num_units=num_units, instrument=instrument, price=price,
                                 expiry=expiry, strategy_name=strategy_name))

    def make_market_order(self, order_decision, market_order):
        SUPPORTED_ORDER_TYPES = (SIDE_SELL, SIDE_BUY)

        if order_decision is not SIDE_STAY and market_order.units <= 0:
            return {}

        elif order_decision in SUPPORTED_ORDER_TYPES:
            order_response = self.broker.make_order(market_order)
            self.invested = MAP_ORDER_TYPES[order_decision]
            self.num_orders += 1

        elif order_decision == SIDE_STAY:
            return {}

        else:
            raise StrategyException

        return order_response

    def update_orders(self, order_response):
        if not order_response:
            return

        trades_opened = order_response.get('tradeOpened')
        trades_closed = order_response.get('tradesClosed')
        price = order_response.get('price')

        if trades_opened or trades_closed:
            portfolio_update = normalize_portfolio_update({'opened': trades_opened, 'closed': trades_closed,
                                                           'price': price})
            self.strategy.update_portfolio(portfolio_update)

        else:
            raise LiveTradingException

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



