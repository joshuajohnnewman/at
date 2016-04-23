import time

from trading.algorithms import ORDER_STAY
from trading.util.log import Logger


class LiveTradingStrategy:
    _logger = None

    def __init__(self, strategy, broker):
        self.ticks = 0
        self.start_time = time.time()

        self.strategy = strategy
        self.interval = strategy.interval
        self.instrument = strategy.instrument

        self.broker = broker

    def tick(self):
        try:
            self.logger.info('Tick Number: {tick}'.format(tick=self.ticks))

            market_data = self.broker.get_historical_price_data(self.instrument, self.strategy.data_window)
            self.strategy.analyze_data(market_data)
            order_decision, market_order = self.strategy.make_decision()

            self.logger.info('Strategy Decison {decision} and market order {order}'
                             .format(decision=order_decision, order=market_order))

            if order_decision is not ORDER_STAY:
                order_response = self.broker.make_order(market_order)
                self.strategy.update_portfolio(order_response)

            time.sleep(self.interval)
            self.ticks += 1
            self.tick()

        # Todo make custom exceptions
        except (KeyboardInterrupt, SystemExit) as e:
            self.logger.error('Manually Stopped Live Trading', data=e)
            self.shutdown('KEYBOARD INTERRUPT')
        except Exception as e:
            self.logger.error('Live Trading Error', data=e)
            self.shutdown(e)

    def shutdown(self, e):
        self.end_time = time.time()
        self.strategy.shutdown(self.start_time, self.end_time, self.ticks, str(e))
        self.logger.info('Shut down live trading strategy successfully')


    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



