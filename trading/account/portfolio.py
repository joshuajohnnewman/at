from trading.account.pair import Pair, PrimaryPair
from trading.util.log import Logger


class Portfolio:

    _logger = None

    def __init__(self, instrument, base_pair, quote_pair):
        self.base_pair = Pair(base_pair['currency'], base_pair['starting_units'], base_pair['tradeable_units'])
        self.quote_pair = Pair(quote_pair['currency'], 0, 0)
        self.primary_pair = PrimaryPair(base_pair['currency'], quote_pair['currency'])

        self.instrument = instrument
        self.profit = 0
        self.percent_profit = 0

    def __repr__(self):
        representation = 'Instrument {instrument} Profit {profit} Percent Gain {percent_profit} Base Pair: {pa} Quote Pair: {pb}'\
            .format(instrument=self.instrument, profit=self.profit, percent_profit=self.percent_profit, pa=self.base_pair, pb=self.quote_pair)
        return representation

    def serialize(self):
        return {
            'profit': self.profit,
            'base_pair': self.base_pair,
            'quote_pair': self.quote_pair,
            'instrument': self.instrument
        }

    def update(self, order_responses):
        closed = order_responses.get('closed', [])
        opened = order_responses.get('opened', [])
        price = order_responses['price']

        self.update_open_positions(price, opened)
        self.update_closed_positions(price, closed)

        hypothetical_profit_total = ((self.quote_pair.tradeable_units / price) + self.base_pair.tradeable_units) - self.base_pair.starting_units

        self.profit = hypothetical_profit_total
        self.percent_profit = (self.profit / self.base_pair.starting_units) * 100

    def update_open_positions(self, price, opened_orders):
        """
        Buy
        :param price:
        :param opened_orders:
        :return:
        """
        for order in opened_orders:
            self.logger.debug('Opened Order', data=order)
            units_bought = order['units'] # Number of units bought

            trade_cost = units_bought * price

            self.logger.info('Updating portfolio for open position trade with old portfolio {portfolio}'
                             .format(portfolio=self), data=order)

            self.base_pair.tradeable_units -=trade_cost
            self.quote_pair.tradeable_units +=units_bought

            self.logger.info('New Portfolio value {portfolio}'.format(portfolio=self), data=order)

    def update_closed_positions(self, price, closed_orders):
        """
        Sell
        :param price:
        :param closed_orders:
        :return:
        """
        for order in closed_orders:
            units_sold = order['units'] # Number of units sold
            self.logger.debug('Closed Order', data=order)

            self.logger.info('Updating portfolio for closed position trade with old portfolio {portfolio}'
                             .format(portfolio=self), data=order)

            trade_gain = units_sold / price

            self.quote_pair.tradeable_units -=units_sold
            self.base_pair.tradeable_units +=trade_gain

            self.logger.info('New Portfolio value {portfolio}'.format(portfolio=self), data=order)

    def update_account_portfolio_data(self, account_information):
        current_account_balance = account_information['balance']

        self.logger.debug('Broker balance {bbalance} vs portfolio balance {pbalance}'
                          .format(bbalance=current_account_balance, pbalance=self.base_pair.tradeable_units))

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger
