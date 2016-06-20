from trading.constants.order import SIDE_STAY
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
        for period in range(0, self.period_count):
            market_data = self.strategy_data[period:self.strategy.data_window]

            self.logger.info('Tick Number: {tick}'.format(tick=self.ticks))
            self.strategy.analyze_data(market_data)
            order_decision, market_order = self.strategy.make_decision()

            self.logger.info('Order decision {decision} and market order {order}'
                            .format(decision=order_decision, order=market_order))

            if order_decision is not SIDE_STAY:
                self.strategy.update_portfolio(market_order)

            self.data[period] = {
               'decision': order_decision,
               'short_term_ma': self.strategy.strategy_data['short_term_ma'],
               'long_term_ma': self.strategy.strategy_data['long_term_ma']
           }

            self.ticks += 1

        return self.data

    def format_data(self, strategy_data):
        return strategy_data['candles']

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger



