import math
from decimal import Decimal

from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.broker import SIDE_BUY, SIDE_SELL, SIDE_STAY, PRICE_ASK_CLOSE, PRICE_ASK_HIGH, PRICE_ASK_LOW, PRICE_ASK
from trading.broker.constants import GRANULARITY_TEN_MINUTE
from trading.constants.constants.interval import INTERVAL_FORTY_CANDLES
from trading.indicators.misc import calc_chandalier_exits
from trading.indicators.overlap_studies import calc_moving_average
from trading.indicators.price_transformation import calc_standard_deviation
from trading.util.transformations import normalize_price_data, normalize_current_price_data


class Josh(Strategy):
    name = 'Josh'

    granularity = GRANULARITY_TEN_MINUTE
    long_exit_sensitivity = 10
    short_exit_sensitivity = 5

    def __init__(self, config):
        strategy_id = config.get('strategy_id')

        if strategy_id is None:
            strategy_id = ObjectId()
        else:
            config = self.load_strategy(strategy_id)

        super(Josh, self).__init__(strategy_id, config)
        self.invested = False

    def calc_units_to_buy(self, current_price):
        base_pair_tradeable_units = self.portfolio.base_pair.tradeable_units
        num_units = math.floor(base_pair_tradeable_units / current_price)
        return int(num_units)

    def calc_units_to_sell(self, current_price):
        quote_pair_tradeable_units = self.portfolio.quote_pair.tradeable_units
        return int(quote_pair_tradeable_units)

    def allocate_tradeable_amount(self):
        base_pair = self.portfolio.base_pair
        profit = self.portfolio.profit

        if profit > 0:
            base_pair.tradeable_units = base_pair.starting_units

    def analyze_data(self, market_data):
        current_market_data = market_data['current']
        historical_market_data = market_data['historical']

        historical_candle_data = historical_market_data['candles']
        asking_price = normalize_current_price_data(current_market_data, PRICE_ASK)

        closing_market_data = normalize_price_data(historical_candle_data, PRICE_ASK_CLOSE)
        high_market_data = normalize_price_data(historical_candle_data, PRICE_ASK_HIGH)
        low_market_data = normalize_price_data(historical_candle_data, PRICE_ASK_LOW)

        std = Decimal(calc_standard_deviation(closing_market_data, min(INTERVAL_FORTY_CANDLES, len(market_data))))

        # Construct the upper and lower Bollinger Bands
        ma = Decimal(calc_moving_average(closing_market_data, min(INTERVAL_FORTY_CANDLES, len(market_data))))
        upper = ma + (Decimal(2) * std)
        lower = ma - (Decimal(2) * std)

        long_exit, short_exit = calc_chandalier_exits(closing_market_data, high_market_data, low_market_data)

        self.strategy_data['asking_price'] = asking_price
        self.strategy_data['long_candle_exit'] = long_exit
        self.strategy_data['short_candle_exit'] = short_exit
        self.strategy_data['lower_bound_ma'] = lower
        self.strategy_data['upper_bound_ma'] = upper

        self.log_strategy_data()

    def make_decision(self):
        asking_price = self.strategy_data['asking_price']
        long_candle_exit = self.strategy_data['long_candle_exit']
        short_candle_exit = self.strategy_data['short_candle_exit']
        lower_bound_ma = self.strategy_data['lower_bound_ma']
        upper_bound_ma = self.strategy_data['upper_bound_ma']

        candle_exit = self._check_candle_exits(asking_price, long_candle_exit, short_candle_exit)

        order_decision = SIDE_STAY
        order = None

        if asking_price < (long_candle_exit - self.long_exit_sensitivity):
            order_decision = SIDE_SELL
            order = self.make_order(asking_price, order_side=order_decision)

        if asking_price > (short_candle_exit + self.short_exit_sensitivity):
            order_decision = SIDE_BUY
            order = self.make_order(asking_price, order_side=order_decision)

        # Look at mean reversion
        if asking_price < lower_bound_ma and (not self.invested and candle_exit == SIDE_BUY):
            # The price has dropped below the lower BB: Buy
            order_decision = SIDE_BUY
            order = self.make_order(asking_price, order_side=order_decision)

        elif asking_price > upper_bound_ma and (self.invested and candle_exit == SIDE_SELL):
            # The price has risen above the upper BB: Sell
            order_decision = SIDE_SELL
            order = self.make_order(asking_price, order_side=order_decision)

        return order_decision, order

    @staticmethod
    def _check_candle_exits(asking_price, long_candle_exit, short_candle_exit):
        if asking_price < long_candle_exit:
            return SIDE_SELL
        elif asking_price > short_candle_exit:
            return SIDE_BUY
        else:
            return SIDE_STAY
