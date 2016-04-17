from bson import ObjectId

from trading.algorithms.base import Strategy
from trading.classifier.random_forest import RFClassifier


class RandomStumps(Strategy):
    name = 'RandomStumps'

    _classifier = None

    def __init__(self, primary_pair, starting_currency, instrument):
        super(RandomStumps, self).__init__(primary_pair, starting_currency, instrument)
        self.invested = False

    def calc_amount_to_buy(self, current_price):
        return self.portfolio.pair_a['tradeable_currency'] / current_price

    def calc_amount_to_sell(self, current_price):
        return self.portfolio.pair_b['tradeable_currency']  # Sell All

    def allocate_tradeable_amount(self):
        pair_a = self.portfolio.pair_a
        profit = self.portfolio.profit
        if profit > 0:
            pair_a['tradeable_currency'] = pair_a['initial_currency']

    def analyze_data(self, current_data, historical_data):
        pass

    def make_decision(self):
        X = self.strategy_data
        prediction = self.classifier.predict(X)
        return prediction

    def make_buy_order(self, current_price):
        pass

    def make_sell_order(self, current_price):
        pass

    def update_portfolio(self, order_response):
        self.logger.info('Order Response')

    def shutdown_strategy(self):
        serialized_classifier = self.classifier.serialize_classifier()
        query = {'_id': ObjectId(serialized_classifier['_id'])}
        update = {'$set': {'classifier': serialized_classifier}}
        self.db.update(query, update)

    def _normalize_price_data(self, price_data, target_field='ask'):
        prices = [candle_data[target_field] for candle_data in price_data]
        return prices

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = RFClassifier()
        return self._classifier
