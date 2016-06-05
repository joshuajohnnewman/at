import datetime
import math

from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.algorithms.constants import TREND_NEGATIVE, TREND_POSITIVE
from trading.broker import MarketOrder, ORDER_MARKET, SIDE_BUY, SIDE_SELL, SIDE_STAY, PRICE_ASK, PRICE_ASK_CLOSE, \
    PRICE_ASK_HIGH, PRICE_ASK_LOW, PRICE_ASK_OPEN, VOLUME
from trading.broker.constants import GRANULARITY_TEN_MINUTE
from trading.classifier import RFClassifier
from trading.indicators import INTERVAL_ONE_HUNDRED_CANDLES
from trading.indicators.momentum_indicators import calc_average_directional_movement_index_rating
from trading.util.transformations import normalize_price_data, normalize_current_price_data, get_last_candle_data


class PatternMatch(Strategy):
    name = 'PatternMatch'

    _classifier = None

    data_window = INTERVAL_ONE_HUNDRED_CANDLES
    granularity = GRANULARITY_TEN_MINUTE
    required_volume = 10
    trend_interval = 30

    def __init__(self, config):
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
        base_pair_units = self.portfolio.base_pair.tradeable_units
        num_units = math.floor(base_pair_units / current_price)
        return int(num_units)

    def calc_units_to_sell(self, current_price):
        quote_pair_units = self.portfolio.quote_pair.tradeable_units
        return int(quote_pair_units)

    def allocate_tradeable_amount(self):
        base_pair = self.portfolio.base_pair
        profit = self.portfolio.profit
        if profit > 0:
            base_pair['tradeable_units'] = base_pair['starting_units']

    def analyze_data(self, market_data):
        current_market_data = market_data['current']
        historical_market_data = market_data['historical']
        historical_candle_data = historical_market_data['candles']

        asking_price = normalize_current_price_data(current_market_data, PRICE_ASK)

        closing_candle_data = normalize_price_data(historical_candle_data, PRICE_ASK_CLOSE)
        high_candle_data = normalize_price_data(historical_candle_data, PRICE_ASK_HIGH)
        low_candle_data = normalize_price_data(historical_candle_data, PRICE_ASK_LOW)

        last_candle = get_last_candle_data(historical_candle_data)

        current_low = last_candle[PRICE_ASK_LOW]
        current_high = last_candle[PRICE_ASK_HIGH]
        current_close = last_candle[PRICE_ASK_CLOSE]
        current_open = last_candle[PRICE_ASK_OPEN]
        current_volume = last_candle[VOLUME]

        trend_direction, trend_strength = self.calculate_trend(high_candle_data, low_candle_data, closing_candle_data)
        self.strategy_data['volume'] = current_volume
        self.strategy_data['trend'] = trend_direction
        self.strategy_data['trend_strength'] = trend_strength
        self.strategy_data['asking']  = asking_price

        X = {
            'open': current_open,
            'close': current_close,
            'high': current_high,
            'low': current_low
        }

        market_prediction = self.classifier.predict(X, format_data=True, unwrap_prediction=True)
        pattern = market_prediction.decision
        self.logger.info('Classifier Decision {prediction}'.format(prediction=market_prediction))
        self.strategy_data['pattern'] = pattern
        self.log_strategy_data()

    def make_decision(self):
        asking_price = self.strategy_data['asking']
        volume = self.strategy_data['volume']
        trend = self.strategy_data['trend']
        pattern = self.strategy_data['pattern']

        decision = SIDE_STAY
        order = None

        if trend == TREND_POSITIVE and volume > self.required_volume and pattern == SIDE_BUY:
            order = self.make_order(asking_price, SIDE_BUY)
            decision = SIDE_BUY
        elif trend == TREND_NEGATIVE and volume > self.required_volume and pattern == SIDE_SELL:
            order = self.make_order(asking_price, SIDE_SELL)
            decision = SIDE_STAY

        return decision, order

    def make_order(self, asking_price, order_side=SIDE_BUY):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat('T') + 'Z'

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

        base_pair = self.portfolio.base_pair
        quote_pair = self.portfolio.quote_pair

        config = {
            'instrument': self.portfolio.instrument,
            'base_pair': {'currency': base_pair.currency, 'starting_units': base_pair.starting_units,
                       'tradeable_units': base_pair.tradeable_units},
            'quote_pair': {'currency': quote_pair.currency, 'starting_units': quote_pair.starting_units,
                       'tradeable_units': quote_pair.tradeable_units}
        }

        strategy = {
            'config': config,
            'profit': self.portfolio.profit,
            'data_window': self.data_window,
            'interval': self.interval,
            'indicators': self.strategy_data.keys(),
            'instrument': self.instrument,
        }

        strategy_query = {'_id': ObjectId(self.strategy_id)}
        strategy_update = {'$set': {'strategy_data': strategy}, '$push': {'sessions': session_info}}
        serialized_classifier = self.classifier.serialize()

        classifier_query = {'_id': ObjectId(self.classifier.classifier_id)}
        classifier_update = {'$set': {'classifier': serialized_classifier}}

        self.db.strategires.update(strategy_query, strategy_update)
        self.db.classifiers.update(classifier_query, classifier_update)

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



