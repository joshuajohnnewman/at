import datetime

from decimal import Decimal
from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.algorithms.util import make_trading_session_info
from trading.broker import MarketOrder, ORDER_MARKET, SIDE_BUY
from trading.classifier.random_forest import RFClassifier
from trading.data.transformations import normalize_price_data
from trading.indicators import INTERVAL_TEN_DAYS
from trading.indicators.talib_indicators import calc_ma


class RandomStumps(Strategy):
    name = 'RandomStumps'

    _classifier = None

    def __init__(self, num_ticks, primary_pair, starting_currency, instrument, classifier_id):
        super(RandomStumps, self).__init__(num_ticks, primary_pair, starting_currency, instrument)
        self.invested = False
        self.classifier_id = classifier_id
        self.classifier

    def calc_amount_to_buy(self, current_price):
        return self.portfolio.pair_a['tradeable_currency'] / current_price

    def calc_amount_to_sell(self, current_price):
        return self.portfolio.pair_b['tradeable_currency']  # Sell All

    def allocate_tradeable_amount(self):
        pair_a = self.portfolio.pair_a
        profit = self.portfolio.profit
        if profit > 0:
            pair_a['tradeable_currency'] = pair_a['initial_currency']

    def analyze_data(self, market_data):
        closing_market_data = normalize_price_data(market_data, 'closeAsk')

        # Construct the upper and lower Bollinger Bands
        short_ma = Decimal(calc_ma(closing_market_data, INTERVAL_TEN_DAYS))
        long_ma = Decimal(calc_ma(closing_market_data, 20))

        self.strategy_data['asking_price'] = closing_market_data[-1]
        self.strategy_data['short_term_ma'] = short_ma
        self.strategy_data['long_term_ma'] = long_ma

    def make_decision(self):
        X = self.strategy_data
        prediction = self.classifier.predict(X, format_data=True, unwrap_prediction=True)
        return prediction

    def make_order(self, asking_price, order_side=SIDE_BUY):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"

        if order_side == SIDE_BUY:
            units = self.calc_amount_to_buy(asking_price)
        else:
            units = self.calc_amount_to_sell(asking_price)

        instrument = self.portfolio.instrument
        side = order_side
        order_type = ORDER_MARKET
        price = asking_price
        expiry = trade_expire

        return MarketOrder(instrument, units, side, order_type, price, expiry)

    def update_portfolio(self, order_response):
        self.logger.info('Order Response')

    def shutdown(self, started_at, ended_at, num_ticks, shutdown_cause):
        serialized_portfolio = self.portfolio.serialize()

        session_info = make_trading_session_info(started_at, ended_at, num_ticks, shutdown_cause)

        strategy = {
            'portfolio': serialized_portfolio,
            'classifier_id': self.classifier.classifier_id,
            'num_ticks': self.num_ticks,
            'interval': self.interval,
            'data_window': self.data_window,
            'indicators': self.strategy_data.keys(),
            'instrument': self.instrument
        }

        query = {'_id': ObjectId(self.id)}
        update = {'$set': {'strategy_data': strategy}, '$push': {'sessions': session_info}}

        classifier_query = {'_id': ObjectId(self.classifier.classifier_id)}
        serialized_classifier = self.classifier.serialize()

        self.db.strategies.update(query, update)
        self.db.classifiers.update(classifier_query, serialized_classifier)

    def _normalize_price_data(self, price_data, target_field='ask'):
        prices = [candle_data[target_field] for candle_data in price_data]
        return prices

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = RFClassifier()
        return self._classifier
