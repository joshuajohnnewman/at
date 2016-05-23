import datetime
import math

from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.algorithms.constants import TREND_NEGATIVE, TREND_POSITIVE
from trading.indicators.momentum_indicators import calc_average_directional_movement_index_rating
from trading.classifier import RFClassifier
from trading.broker import MarketOrder, ORDER_MARKET, SIDE_BUY, SIDE_SELL, SIDE_STAY, PRICE_ASK_CLOSE, \
    PRICE_ASK_HIGH, PRICE_ASK_LOW, PRICE_ASK_OPEN, VOLUME
from trading.data.transformations import normalize_price_data, normalize_current_price_data


class PatternMatch(Strategy):
    name = 'Moving Average Crossover'

    _classifier = None
    required_volume = 10
    trend_interval = 30

    def __init__(self, config):
        self.target_pattern = config.get('target_pattern')
        strategy_id = config.get('strategy_id')

        if strategy_id is None:
            strategy_id = ObjectId()
        else:
            config = self.load_strategy(strategy_id)

        super(PatternMatch, self).__init__(config)
        self.strategy_id = strategy_id
        self.classifier_config = config['classifier_config']
        self.invested = False

    def calc_units_to_buy(self, current_price):
        pair_a_tradeable = self.portfolio.pair_a.tradeable_currency
        num_units = math.floor(pair_a_tradeable / current_price)
        return int(num_units)

    def calc_units_to_sell(self, current_price):
        pair_b_tradeable = self.portfolio.pair_b.tradeable_currency
        return pair_b_tradeable

    def allocate_tradeable_amount(self):
        pair_a = self.portfolio.pair_a
        profit = self.portfolio.profit
        if profit > 0:
            pair_a['tradeable_currency'] = pair_a['initial_currency']

    def analyze_data(self, market_data):
        current_market_data = market_data['current']
        historical_market_data = market_data['historical']
        historical_candle_data = historical_market_data['candles']

        asking_price = normalize_current_price_data(current_market_data)

        closing_candle_data = normalize_price_data(historical_candle_data, PRICE_ASK_CLOSE)
        opening_candle_data = normalize_price_data(historical_candle_data, PRICE_ASK_OPEN)
        high_candle_data = normalize_price_data(historical_candle_data, PRICE_ASK_HIGH)
        low_candle_data = normalize_price_data(historical_candle_data, PRICE_ASK_LOW)
        volume_candle_data = normalize_price_data(historical_candle_data, VOLUME)

        trend_direction, trend_strength = self.calculate_trend(high_candle_data, low_candle_data, closing_candle_data)
        self.strategy_data['volume'] = volume_candle_data
        self.strategy_data['trend'] = trend_direction
        self.strategy_data['trend_strength'] = trend_strength
        self.strategy_data['asking']  = asking_price

        X = {
            'open': opening_candle_data,
            'close': closing_candle_data,
            'high': high_candle_data,
            'low': low_candle_data
        }

        market_prediction = self.classifier.predict(X, format_data=True, unwrap_prediction=True)
        pattern = market_prediction.decision


        self.strategy_data['pattern'] = pattern

        self.log_strategy_data()

    def make_decision(self):
        asking_price = self.strategy_data['asking']
        volume = self.strategy_data['volume']
        trend = self.strategy_data['trend']
        pattern = self.strategy_data['pattern']

        decision = SIDE_STAY
        order = None

        if trend == TREND_POSITIVE and volume > self.required_volume and pattern == self.target_pattern:
            order = self.make_order(asking_price, SIDE_BUY)
        elif trend == TREND_NEGATIVE and volume > self.required_volume and pattern == self.target_pattern:
            order = self.make_order(asking_price, SIDE_SELL)

        return decision, order

    def make_order(self, asking_price, order_side=SIDE_BUY):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"

        if order_side == SIDE_BUY:
            units = self.calc_units_to_buy(asking_price)
        else:
            units = self.calc_units_to_sell(asking_price)

        instrument = self.portfolio.instrument
        side = order_side
        order_type = ORDER_MARKET
        price = asking_price
        expiry = trade_expire

        return MarketOrder(instrument, units, side, order_type, price, expiry)

    def shutdown(self, started_at, ended_at, num_ticks, num_orders, shutdown_cause):
        session_info = self.make_trading_session_info(started_at, ended_at, num_ticks, num_orders, shutdown_cause)

        pair_a = self.portfolio.pair_a
        pair_b = self.portfolio.pair_b

        config = {
            'instrument': self.portfolio.instrument,
            'pair_a': {'name': pair_a.name, 'starting_currency': pair_a.starting_currency,
                       'tradeable_currency': pair_a.tradeable_currency},
            'pair_b': {'name': pair_b.name, 'starting_currency': pair_b.starting_currency,
                       'tradeable_currency': pair_b.tradeable_currency}
        }

        strategy = {
            'config': config,
            'profit': self.portfolio.profit,
            'data_window': self.data_window,
            'interval': self.interval,
            'indicators': self.strategy_data.keys(),
            'instrument': self.instrument,
        }

        query = {'_id': ObjectId(self.strategy_id)}
        update = {'$set': {'strategy_data': strategy}, '$push': {'sessions': session_info}}

        classifier_query = {'_id': ObjectId(self.classifier.classifier_id)}
        serialized_classifier = self.classifier.serialize()

        self.db.strategies.update(query, update, upsert=True)
        self.db.classifiers.update(classifier_query, serialized_classifier)

    def calculate_trend(self, high, low, close):
        trend_start_low = low[self.trend_interval]
        trend_end_low = low[-1]

        if trend_end_low > trend_start_low:
            trend_direction = TREND_POSITIVE
        else:
            trend_direction = TREND_NEGATIVE

        trend_strength = calc_average_directional_movement_index_rating(high=high, low=low, close=close,
                                                                        interval=self.trend_interval)

        return trend_direction, trend_strength

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = RFClassifier(self.classifier_config)
        return self._classifier



