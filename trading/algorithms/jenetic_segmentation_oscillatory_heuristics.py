from trading.algorithms import ORDER_BUY, ORDER_SELL, ORDER_STAY
from trading.algorithms.base import Strategy


class Josh(Strategy):

    _tradeable_currency = None

    def __init__(self, primary_pair, ):
        super(Josh).__init__(primary_pair)

    def calc_amount_to_buy(self):
        pass

    def calc_amount_to_sell(self):
        pass

    def allocate_tradeable_amount(self):
        pass

    def make_decision(self, data):
        LONG_EXIT_SENSITIVITY = 10
        SHORT_EXIT_SENSITIVITY = 5

        closing_price = self.strategy_data['closing_price']
        long_candle_exit = self.strategy_data['long_candle_exit']
        short_candle_exit = self.strategy_data['short_candle_exit']
        lower_bound_ma = self.strategy_data['lower_bound_ma']
        upper_bound_ma = self.strategy_data['upper_bound_ma']


        candle_exit = self._check_candle_exits(closing_price, long_candle_exit, short_candle_exit)

        order_decision = ORDER_STAY
        order = None

        if candle_exit is not None:
            self.logger.info('Candle exit decision {dec}'.format(dec=candle_exit))

        if closing_price < (long_candle_exit - LONG_EXIT_SENSITIVITY):
            order_decision = ORDER_SELL
            order = self.make_sell_order()

        if closing_price > (short_candle_exit + SHORT_EXIT_SENSITIVITY):
            order_decision = ORDER_BUY
            order = self.make_buy_oder()

        # Look at mean reversion
        if closing_price < lower_bound_ma and not self.invested and candle_exit == ORDER_BUY:
            # The price has dropped below the lower BB, so buy
            order_decision = ORDER_BUY
            order = self.make_buy_order()

        elif closing_price > upper_bound_ma and self.invested and candle_exit == ORDER_SELL:
            # The price has risen above the upper BB, so sell
            order_decision = ORDER_SELL
            order = self.make_sell_order()

        return order_decision, order

    def analyze_data(self, data):
        pass

    def make_buy_order(self):
        return {}

    def make_sell_order(self):
        return {}

    def _check_candle_exits(self, closing_price, long_candle_exit, short_candle_exit):
        if closing_price < long_candle_exit:
            return ORDER_SELL
        elif closing_price > short_candle_exit:
            return ORDER_BUY
        else:
            return ORDER_STAY