import datetime

from decimal import Decimal

from trading.algorithms.base import Strategy
from trading.broker import MarketOrder, ORDER_MARKET, SIDE_BUY, SIDE_SELL, SIDE_STAY
from trading.data.transformations import normalize_price_data
from trading.indicators import INTERVAL_TEN_DAYS, INTERVAL_NINETY_DAYS
from trading.indicators.talib_indicators import calc_ma


class MAC(Strategy):
    name = 'Moving Average Crossover'

    crossover_threshold = 0.005

    def __init__(self, primary_pair, starting_currency, instrument):
        super(MAC, self).__init__(primary_pair, starting_currency, instrument)
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

    def analyze_data(self, market_data):
        market_data = market_data['candles']
        closing_market_data = normalize_price_data(market_data, 'closeAsk')

        # Construct the upper and lower Bollinger Bands
        short_ma = Decimal(calc_ma(closing_market_data, INTERVAL_TEN_DAYS))
        long_ma = Decimal(calc_ma(closing_market_data, INTERVAL_NINETY_DAYS))

        self.strategy_data['short_term_ma'] = short_ma
        self.strategy_data['long_term_ma'] = long_ma

    def make_decision(self):
        short_term = self.strategy_data['short_term_ma']
        long_term = self.strategy_data['long_term_ma']

        diff = 100 * (short_term - long_term) / ((short_term + long_term) / 2)

        decision = SIDE_STAY
        order = None

        if diff >= self.crossover_threshold and not self.invested:
            decision = SIDE_BUY
            order = self.make_order(decision)

        elif diff <= - self.crossover_threshold and self.invested:
            decision = SIDE_SELL
            order = self.make_order(decision)

        return decision, order

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


