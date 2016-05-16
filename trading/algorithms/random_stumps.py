import datetime
import math

from decimal import Decimal
from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.broker import MarketOrder, ORDER_MARKET, SIDE_BUY, SIDE_SELL, SIDE_STAY
from trading.classifier.random_forest import RFClassifier
from trading.data.transformations import normalize_price_data
from trading.indicators import INTERVAL_TEN_DAYS
from trading.indicators.overlap_studies import calc_moving_average


class RandomStumps(Strategy):
    name = 'RandomStumps'

    _classifier = None

    def __init__(self, config):
        strategy_id = config.get('strategy_id')

        if strategy_id is None:
            self.strategy_id = ObjectId()
        else:
            config = self.load_strategy(strategy_id)

        super(RandomStumps, self).__init__(config)
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
            pair_a.tradeable_currency = pair_a.starting_currency

    def analyze_data(self, market_data):
        market_data = market_data['candles']
        closing_market_data = normalize_price_data(market_data, 'closeAsk')

        # Construct the upper and lower Bollinger Bands
        short_ma = Decimal(calc_moving_average(closing_market_data, INTERVAL_TEN_DAYS))
        long_ma = Decimal(calc_moving_average(closing_market_data, 20))

        self.strategy_data['asking_price'] = closing_market_data[-1]
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

        if units <= 0:
            return None
        else:
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

    @staticmethod
    def _normalize_price_data(price_data, target_field='ask'):
        prices = [candle_data[target_field] for candle_data in price_data]
        return prices

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = RFClassifier(self.classifier_config)
        return self._classifier
