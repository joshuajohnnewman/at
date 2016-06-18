import datetime
import time

from trading.algorithms import initialize_strategy, ORDER_BUY, ORDER_SELL, ORDER_STAY
from trading.broker import PRICE_ASK
from trading.live_trading.exceptions import LiveTradingException, KeyboardInterruptMessage, StrategyException
from trading.live_trading.util import invested_map, normalize_portfolio_update
from trading.util.log import Logger
from trading.util.transformations import normalize_current_price_data


class BacktestTradingStrategy:
    orders = {}
    invested = False

    _logger = None

    def __init__(self, strategy_config, broker, backtest_count):
        self.tick_num = 0
        self.num_orders = 0
        self.backtest_count = backtest_count
        self.start_time = time.time()

        self.broker = broker
        account_information = self.broker.get_account_information()

        self.strategy = initialize_strategy(strategy_config, account_information)
        self.interval = self.strategy.interval
        self.instrument = self.strategy.instrument

        broker.get_backtest_price_data(self.instrument, backtest_count, self.strategy.granularity)

    def tick(self):
        while self.tick_num < self.backtest_count:
            try:
                self.logger.info('Tick Number: {tick}'.format(tick=self.tick_num))
                account_information = self.broker.get_account_information()
                self.strategy.portfolio.update_account_portfolio_data(account_information)

                self.logger.info('Current Portfolio {portfolio}'.format(portfolio=self.strategy.portfolio))
                self.logger.debug('Account Info', data=account_information)

                order_responses = self.get_order_updates()

                if order_responses:
                    self.logger.info('Order Responses', data=order_responses)
                    self.strategy.update_portfolio(order_responses)
                    order_ids = order_responses.keys()
                    self.remove_recorded_orders(order_ids)

                historical_market_data = self.broker.get_historical_price_data(self.instrument,
                                                                               count=self.strategy.data_window,
                                                                               granularity=self.strategy.granularity,
                                                                               tick=self.tick_num)

                current_market_data = self.broker.get_current_price_data(instrument=self.instrument, tick=self.tick_num)

                self.strategy.analyze_data({
                    'historical': historical_market_data,
                    'current': current_market_data
                })

                order_decision, market_order = self.strategy.make_decision()
                order_response = self.make_market_order(order_decision, market_order)

                self.update_orders(order_response)

                self.tick_num += 1

            except (KeyboardInterrupt, SystemExit) as e:
                self.logger.error('Manually Stopped Live Trading', data=e)
                self.shutdown(KeyboardInterruptMessage)
                break
            except LiveTradingException as e:
                self.logger.error('Live Trading Error', data=e)
                self.shutdown(e)
                break
            except Exception as e:
                self.logger.error('Uncaught Error', data=e)
                self.shutdown(e)
                break

        self.shutdown('End Backtest')
        self.logger.info('Trading Results: Account {account}'.format(account=self.broker.account))
        self.logger.info('Trading Results: Portfolio {portfolio}'.format(portfolio=self.strategy.portfolio))
        self.logger.info('Trading Results: Num Orders {num_orders}'.format(num_orders=self.num_orders))

    def get_order_updates(self):
        order_ids = self.orders.keys()
        order_info_map = {}

        for order_id in order_ids:
            try:
                order_information = self.broker.get_order(order_id)
                self.logger.info('Order Info for order {order_id} {order_information}'
                                 .format(order_id=order_id, order_information=order_information))

                if order_information.get('tradeOpened'):
                    order_info_map[order_id] = order_information
                else:
                    self.logger.info('Order {order_id} not filled yet'.format(order_id=order_id))
            except Exception as e:
                print e

        self.logger.info('Current Orders', data=order_info_map)
        return order_info_map

    def remove_recorded_orders(self, order_ids):
        for order_id in order_ids:
            self.logger.info('Deleting order', data=order_id)
            del self.orders[order_id]

    def shutdown(self, e):
        end_time = time.time()

        if self.invested:
            self.logger.info('Currently Invested, closing out all open positions')
            current_market_data = self.broker.get_current_price_data(instrument=self.instrument, tick=self.tick_num)
            asking_price =  normalize_current_price_data(current_market_data, target_field=PRICE_ASK)
            sell_order = self.strategy.make_order(asking_price, order_side=ORDER_SELL)
            order_response = self.make_market_order(ORDER_SELL, sell_order)
            self.update_orders(order_response)

        self.strategy.shutdown(self.start_time, end_time, self.tick_num, self.num_orders, str(e))
        self.logger.info('Shut down live trading strategy successfully')

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
        self.logger.info('Strategy Decision: {decision}'.format(decision=order_decision))
        self.logger.info('Market Order {order}'.format(order=market_order))

        if order_decision in (ORDER_SELL, ORDER_BUY):
            order_response = self.broker.make_order(market_order)
            self.invested = invested_map[order_decision]
            self.num_orders += 1

        elif order_decision == ORDER_STAY:
            return {}

        else:
            self.logger.error('Unsupported order type', data=order_decision)
            raise StrategyException

        return order_response

    def update_orders(self, order_response):
        self.logger.info('Order response {order}'.format(order=order_response))
        trades_opened = order_response.get('tradeOpened')
        trades_closed = order_response.get('tradesClosed')
        price = order_response.get('price')

        if not order_response:
            self.logger.info('No Order Response')
            return

        elif trades_opened or trades_closed:
            portfolio_update = normalize_portfolio_update({'opened': trades_opened, 'closed': trades_closed, 'price': price})
            self.strategy.update_portfolio(portfolio_update)

        else:
            self.logger.debug('Unhandled order response')
            raise LiveTradingException

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



