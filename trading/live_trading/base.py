import time

from trading.algorithms import ORDER_STAY
from trading.util.log import Logger


class LiveTradingStrategy:
    _logger = None

    def __init__(self, strategy, broker):
        self.ticks = 0
        self.strategy = strategy
        self.interval = strategy.interval
        self.instrument = strategy.instrument

        self.broker = broker

    def tick(self):
        try:
            self.logger.info('Tick Number: {tick}'.format(tick=self.ticks))

            current_data = self.broker.get_current_price_data(self.instrument)
            past_data = self.broker.get_historical_price_data(self.instrument, self.strategy.data_window)
            self.strategy.analyze_data(current_data, past_data)
            order_decision, market_order = self.strategy.make_decision()

            if order_decision is not ORDER_STAY:
                order_response = self.broker.make_order(market_order)
                self.strategy.update_portfolio(order_response)

            time.sleep(self.interval)
            self.ticks += 1
            self.tick()

        # Todo make custom exceptions
        except Exception as e:
            self.logger.error('Live Trading Error', data=e)
            self.strategy.shutdown()

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



