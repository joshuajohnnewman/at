import math

from decimal import Decimal
from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.broker import SIDE_BUY, SIDE_SELL, SIDE_STAY, PRICE_ASK_CLOSE, PRICE_ASK
from trading.classifier.random_forest import RFClassifier
from trading.indicators import INTERVAL_TEN_CANDLES, INTERVAL_TWENTY_CANDLES
from trading.indicators.overlap_studies import calc_moving_average
from trading.util.transformations import normalize_price_data, normalize_current_price_data


class RandomStumps(Strategy):
    name = 'RandomStumps'

    features = ['asking_price', 'long_candle_exit', 'short_candle_exit', 'lower_bound_ma', 'upper_bound_ma', 'decision']

    _classifier = None

    def __init__(self, config):
        strategy_id = config.get('strategy_id')

        if strategy_id is None:
            strategy_id = ObjectId()
        else:
            config = self.load_strategy(strategy_id)

        super(RandomStumps, self).__init__(strategy_id, config)

        self.classifier_config = config['classifier_config']
        self.classifier_config['features'] = self.features

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

        # Construct the upper and lower Bollinger Bands
        short_ma = Decimal(calc_moving_average(closing_market_data, INTERVAL_TEN_CANDLES))
        long_ma = Decimal(calc_moving_average(closing_market_data, INTERVAL_TWENTY_CANDLES))

        self.strategy_data['asking_price'] = asking_price
        self.strategy_data['short_term_ma'] = short_ma
        self.strategy_data['long_term_ma'] = long_ma

        self.log_strategy_data()

    def make_decision(self):
        X = self.strategy_data

        market_prediction = self.classifier.predict(X, format_data=True, unwrap_prediction=True)
        decision = market_prediction.decision

        if decision in (SIDE_BUY, SIDE_SELL):
            current_price = self.strategy_data['asking_price']
            order =  self.make_order(current_price, decision)
        else:
            order = None

        if order is None:
            decision = SIDE_STAY

        return decision, order

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = RFClassifier(self.classifier_config)
        return self._classifier
