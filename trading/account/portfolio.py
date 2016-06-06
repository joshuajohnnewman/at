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

    def __repr__(self):
        representation = 'Instrument {instrument} Profit {profit} Base Pair: {pa} Quote Pair: {pb}'\
            .format(instrument=self.instrument, profit=self.profit, pa=self.base_pair, pb=self.quote_pair)
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

        hypothetical_profit_total = (price * self.quote_pair.tradeable_units) + self.base_pair.tradeable_units

        self.profit = hypothetical_profit_total

    def update_open_positions(self, price, opened_orders):
        for order in opened_orders:
            self.logger.debug('Opened Order', data=order)
            quote_units_bought = order['units']

            trade_cost = quote_units_bought * price

            self.logger.info('Updating portfolio for open position trade with old portfolio {portfolio}'
                             .format(portfolio=self), data=order)

            current_base_units = self.base_pair.tradeable_units
            self.base_pair.tradeable_units = current_base_units - trade_cost
            self.quote_pair.tradeable_units = quote_units_bought

            self.logger.info('New Portfolio value {portfolio}'.format(portfolio=self), data=order)

    def update_closed_positions(self, price, closed_orders):
        for order in closed_orders:
            units = order['units']
            self.logger.debug('Closed Order', data=order)

            self.logger.info('Updating portfolio for closed position trade with old portfolio {portfolio}'
                             .format(portfolio=self), data=order)

            total_traded = units * price

            current_base_units = self.base_pair.tradeable_units
            current_quote_units = self.quote_pair.tradeable_units
            self.quote_pair_tradeable_units = current_quote_units - total_traded
            self.base_pair.tradeable_units = current_base_units + total_traded

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
