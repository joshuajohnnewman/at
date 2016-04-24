import datetime
import math

from bson import ObjectId
from decimal import Decimal

from trading.algorithms.base import Strategy
from trading.broker import MarketOrder, ORDER_MARKET, SIDE_BUY, SIDE_SELL, SIDE_STAY, PRICE_ASK_CLOSE, PRICE_ASK_HIGH, \
    PRICE_LOW_ASK
from trading.data.transformations import normalize_price_data
from trading.indicators.price_transformation import calc_standard_deviation
from trading.indicators.overlap_studies import calc_moving_average
from trading.indicators import calc_chandalier_exits, INTERVAL_FORTY_DAYS


class Josh(Strategy):
    name = 'Josh'

    long_exit_sensitivity = 10
    short_exit_sensitivity = 5

    def __init__(self, config):
        strategy_id = config.get('strategy_id')

        if strategy_id is None:
            strategy_id = ObjectId()
        else:
            config = self.load_strategy(strategy_id)

        super(Josh, self).__init__(config)
        self.strategy_id = strategy_id
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
        closing_market_data = normalize_price_data(market_data, PRICE_ASK_CLOSE)
        high_market_data = normalize_price_data(market_data, PRICE_ASK_HIGH)
        low_market_data = normalize_price_data(market_data, PRICE_LOW_ASK)

        std = Decimal(calc_standard_deviation(closing_market_data, min(INTERVAL_FORTY_DAYS, len(market_data))))

        # Construct the upper and lower Bollinger Bands
        ma = Decimal(calc_moving_average(closing_market_data, min(INTERVAL_FORTY_DAYS, len(market_data))))
        upper = ma + (Decimal(2) * std)
        lower = ma - (Decimal(2) * std)

        long_exit, short_exit = calc_chandalier_exits(closing_market_data, high_market_data, low_market_data)

        self.strategy_data['asking_price'] = closing_market_data[-1]
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

        if candle_exit is not None:
            #self.logger.info('Candle exit decision {dec}'.format(dec=candle_exit))
            pass

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
            'pair_a': {'name': pair_a.name, 'starting_currency': pair_a.starting_currency, 'tradeable_currency': pair_a.tradeable_currency},
            'pair_b': {'name': pair_b.name, 'starting_currency': pair_b.starting_currency, 'tradeable_currency': pair_b.tradeable_currency}
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
        self.db.strategies.update(query, update, upsert=True)

    @staticmethod
    def _check_candle_exits(asking_price, long_candle_exit, short_candle_exit):
        if asking_price < long_candle_exit:
            return SIDE_SELL
        elif asking_price > short_candle_exit:
            return SIDE_BUY
        else:
            return SIDE_STAY
