import math
from decimal import Decimal

from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.broker import SIDE_BUY, SIDE_SELL, SIDE_STAY, PRICE_ASK_CLOSE, PRICE_ASK
from trading.constants.constants.interval import INTERVAL_TWENTY_CANDLES, INTERVAL_TEN_CANDLES
from trading.indicators import INTERVAL_TEN_CANDLES
from trading.indicators.overlap_studies import calc_moving_average
from trading.util.transformations import normalize_price_data, normalize_current_price_data


class MAC(Strategy):
    name = 'Moving Average Crossover'

    crossover_threshold = 0.001

    def __init__(self, config):
        strategy_id = config.get('strategy_id')

        if strategy_id is None:
            strategy_id = ObjectId()
        else:
            config = self.load_strategy(strategy_id)

        super(MAC, self).__init__(config)
        self.strategy_id = strategy_id
        self.invested = False

    def calc_units_to_buy(self, current_price):
        base_pair_tradeable = self.portfolio.base_pair.tradeable_units
        num_units = math.floor(base_pair_tradeable / current_price)
        return int(num_units)

    def calc_units_to_sell(self, current_price):
        quote_pair_tradeable = self.portfolio.quote_pair.tradeable_units
        return int(quote_pair_tradeable)

    def allocate_tradeable_amount(self):
        base_pair = self.portfolio.base_pair
        profit = self.portfolio.profit
        if profit > 0:
            base_pair['tradeable_units'] = base_pair['initial_units']

    def analyze_data(self, market_data):
        current_market_data = market_data['current']
        historical_market_data = market_data['historical']

        historical_candle_data = historical_market_data['candles']

        closing_market_data = normalize_price_data(historical_candle_data, PRICE_ASK_CLOSE)
        asking_price = normalize_current_price_data(current_market_data, PRICE_ASK)

        # Construct the upper and lower Bollinger Bands
        short_ma = Decimal(calc_moving_average(closing_market_data, INTERVAL_TEN_CANDLES))
        long_ma = Decimal(calc_moving_average(closing_market_data, INTERVAL_TWENTY_CANDLES))

        self.strategy_data['asking_price'] = asking_price
        self.strategy_data['short_term_ma'] = short_ma
        self.strategy_data['long_term_ma'] = long_ma

        self.log_strategy_data()

    def make_decision(self):
        asking_price = self.strategy_data['asking_price']
        short_term = self.strategy_data['short_term_ma']
        long_term = self.strategy_data['long_term_ma']

        decision = SIDE_STAY
        order = None

        try:
            diff = 100 * (short_term - long_term) / ((short_term + long_term) / 2)

            if diff >= self.crossover_threshold and not self.invested:
                decision = SIDE_BUY
                order = self.make_order(asking_price, decision)

            elif diff <= -self.crossover_threshold and self.invested:
                decision = SIDE_SELL
                order = self.make_order(asking_price, decision)

            else:
                return decision, None
        except Exception as e:
            self.logger.error(e)
            return decision, order

        if order.units <=0:
            decision = SIDE_STAY
            order = None

        return decision, order



