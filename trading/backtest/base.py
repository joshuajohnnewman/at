import time

from trading.algorithms import ORDER_STAY
from trading.backtest import get_historical_data
from trading.util.log import Logger


class BackTestStrategy:
    _logger = None

    def __init__(self, strategy, period_count, backtest_file, granularity):
        self.ticks = 0
        self.strategy = strategy
        self.interval = strategy.interval
        self.instrument = strategy.instrument
        self.period_count = period_count

        historical_data = get_historical_data(backtest_file)
        self.strategy_data = self.format_data(historical_data)

    def tick(self):
            self.logger.info('Tick Number: {tick}'.format(tick=self.ticks))

            current_data = self.broker.get_current_price_data(self.instrument)
            past_data = self.broker.get_historical_price_data(self.instrument, self.strategy.data_window)
            self.strategy.analyze_data(current_data, past_data)
            order_decision, market_order = self.strategy.make_decision()

            if order_decision is not ORDER_STAY:
                self.strategy.update_portfolio(market_order)

            self.ticks += 1
            self.tick()


    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



