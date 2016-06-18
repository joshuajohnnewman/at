import datetime
import time

from abc import abstractmethod, ABCMeta

from trading.algorithms import initialize_strategy, ORDER_BUY, ORDER_SELL, ORDER_STAY
from trading.broker import PRICE_ASK
from trading.live.exceptions import LiveTradingException, StrategyException
from trading.live.util import MAP_ORDER_TYPES, normalize_portfolio_update
from trading.util.log import Logger
from trading.util.transformations import normalize_current_price_data


class TradingStrategyRunner(object):
    __metaclass__ = ABCMeta

    orders = {}
    invested = False

    _logger = None

    def __init__(self, strategy_config, broker):
        self.tick_num = 0
        self.num_orders = 0
        self.start_time = time.time()

        self.broker = broker
        account_information = self.broker.get_account_information()

        self.strategy = initialize_strategy(strategy_config, account_information)
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

    def remove_recorded_orders(self, order_responses):
        order_ids = order_responses.keys()

        for order_id in order_ids:
            del self.orders[order_id]

    def shutdown(self, shutdown_cause):
        shutdown_cause = str(shutdown_cause)
        end_time = time.time()

        if self.invested:
            current_market_data = self.broker.get_current_price_data(instrument=self.instrument)
            asking_price =  normalize_current_price_data(current_market_data, target_field=PRICE_ASK)
            sell_order = self.strategy.make_order(asking_price, order_side=ORDER_SELL)
            order_response = self.make_market_order(ORDER_SELL, sell_order)
            self.update_orders(order_response)

        self.strategy.shutdown(self.start_time, end_time, self.tick_num, self.num_orders, shutdown_cause)

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
        SUPPORTED_ORDER_TYPES = (ORDER_SELL, ORDER_BUY)

        if order_decision in SUPPORTED_ORDER_TYPES:
            order_response = self.broker.make_order(market_order)
            self.invested = MAP_ORDER_TYPES[order_decision]
            self.num_orders += 1

        elif order_decision == ORDER_STAY:
            return {}

        else:
            raise StrategyException

        return order_response

    def update_orders(self, order_response):
        trades_opened = order_response.get('tradeOpened')
        trades_closed = order_response.get('tradesClosed')
        price = order_response.get('price')

        if not order_response:
            return

        elif trades_opened or trades_closed:
            portfolio_update = normalize_portfolio_update({'opened': trades_opened, 'closed': trades_closed, 'price': price})
            self.strategy.update_portfolio(portfolio_update)

        else:
            raise LiveTradingException

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



