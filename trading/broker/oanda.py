import os

from trading.broker.base import Broker


class OandaBroker(Broker):

    _account_id = None
    _oanda = None

    def __init__(self):
        self.account_id = os.environ['OANDA_ACCOUNT_ID']

    def make_order(self, order):
        order_confirmation = self._oanda.create_order(self.account_id,
                                                 instrument=order.instrument,
                                                 units=order.units,
                                                 side=order.side,
                                                 type=order.type,
                                                 price=order.price,
                                                 expiry=order.expiry
                                                 )

        return order_confirmation

    def get_price_data(self, instrument):
        broker_response = self._oanda.get_prices(instruments=instrument)
        return broker_response

    @property
    def oanda(self):
        import oandapy

        if self._oanda is None:
            self._oanda = oandapy.API(environment=os.environ['OANDA_ENV'], access_token=os.environ['OANDA_ACCESS_TOKEN'])
        return self._oanda

