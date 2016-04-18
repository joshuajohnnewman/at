from trading.algorithms import ORDER_STAY
from trading.util.log import Logger


class TrainingStrategy:
    _logger = None
    data = {}

    def __init__(self, strategy, broker, instrument, granularity, period_count):
        self.ticks = 0
        self.strategy = strategy
        self.interval = strategy.interval
        self.instrument = strategy.instrument
        self.period_count = period_count

        self.broker = broker
        historical_data = self.broker.get_historical_price_data(instrument, (period_count + self.strategy.data_window), granularity)
        self.strategy_data = self.format_data(historical_data)

    def tick(self):
        for period in self.period_count:
            current_data = self.strategy_data[period:self.strategy_data]

            self.logger.info('Tick Number: {tick}'.format(tick=self.ticks))
            strategy_data = self.strategy.analyze_data(current_data)
            order_decision, market_order = self.strategy.make_decision()

            if order_decision is not ORDER_STAY:
                self.strategy.update_portfolio(market_order)

            self.data[period] = {
               'decision': order_decision,
               'short_term_ma': strategy_data['short_term_ma'],
               'long_term_ma': strategy_data['long_term_ma']
           }

            self.ticks += 1
            self.tick()

        return self.strategy_data

    def format_data(self, strategy_data):
        return strategy_data['candles']

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



