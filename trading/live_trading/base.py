import datetime
import time

from trading.algorithms import ORDER_STAY
from trading.live_trading.exceptions import LiveTradingException, KeyboardInterruptMessage
from trading.util.log import Logger


class LiveTradingStrategy:
    orders = {}
    _logger = None

    def __init__(self, strategy, broker):
        self.ticks = 0
        self.num_orders = 0
        self.start_time = time.time()

        self.strategy = strategy
        self.interval = strategy.interval
        self.instrument = strategy.instrument

        self.broker = broker

    def tick(self):
        try:
            self.logger.info('Tick Number: {tick}'.format(tick=self.ticks))
            order_ids, order_responses = self.get_order_updates()
            if order_ids:
                self.strategy.update_portfolio(order_responses)

            market_data = self.broker.get_historical_price_data(self.instrument, self.strategy.data_window)
            self.strategy.analyze_data(market_data)
            order_decision, market_order = self.strategy.make_decision()

            self.logger.info('Strategy Decision: {decision}'.format(decision=order_decision))

            if order_decision is not ORDER_STAY:
                self.log_market_order(order_decision, market_order)
                order_response = self.broker.make_order(market_order)
                print(order_response)
                trade_opened = order_response.get('tradeOpened')
                if trade_opened:
                    self.strategy.update_portfolio(order_response)
                else:
                    self.orders[trade_opened['id']] = order_response
                self.num_orders += 1

            time.sleep(self.interval)
            self.ticks += 1
            self.tick()

        except (KeyboardInterrupt, SystemExit) as e:
            self.logger.error('Manually Stopped Live Trading', data=e)
            self.shutdown(KeyboardInterruptMessage)
        except LiveTradingException as e:
            self.logger.error('Live Trading Error', data=e)
            self.shutdown(e)


    def get_order_updates(self):
        order_ids = self.orders.keys()
        order_info_map = {}
        valid_order_ids = []

        for order_id in order_ids:
            try:
                order_information = self.broker.get_order(order_id)
                order_info_map[order_id] = order_information
                valid_order_ids.append(order_id)
            except Exception as e:
                print e

        self.logger.info('Order Map', data=order_info_map)
        return valid_order_ids, order_info_map

    def shutdown(self, e):
        self.end_time = time.time()
        self.strategy.shutdown(self.start_time, self.end_time, self.ticks, self.num_orders, str(e))
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


    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



