import time

from trading.util.log import Logger


class LiveTradingStrategy:
    strategy = None
    broker = None

    _instrument = None
    _interval = None
    _logger = None

    def __init__(self, strategy, broker):
        self.strategy = strategy
        self._interval = strategy.interval
        self._instrument = strategy.instrument

        self.broker = broker

    def tick(self):
        try:
            data = self.broker.get_price_data(self._instrument)
            self.strategy.analyze_data(data)
            market_order = self.strategy.make_decision()

            if market_order:
                order_response = self.broker.make_order(market_order)
                self.strategy.update_portfolio(order_response)

            time.sleep(self._interval)
            self.tick()

        # Todo make custom exceptions
        except Exception as e:
            self.logger.error('Live Trading Error', data=e)

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



