import os

from oandapy.oandapy import EndpointsMixin

from trading.broker.base import Broker
from trading.broker.oanda_constants import GRANULARITY_DAY, COUNT_FORTY


class OandaBroker(Broker, EndpointsMixin):
    name = 'Oanda'

    _account_id = None
    _oanda = None

    def get_current_price_data(self, instrument):
        if not isinstance(instrument, list):
            instrument = [instrument]
        broker_response = self.oanda.get_prices(instruments=instrument)
        return broker_response

    def get_historical_price_data(self, instrument, count=COUNT_FORTY, granularity=GRANULARITY_DAY):
        broker_response = self.oanda.get_history(instrument=instrument, count=count, granularity=granularity)
        return broker_response

    def get_order(self, order_id):
        order_information = self.oanda.get_order(self.account_id, order_id)
        return order_information

    def make_order(self, order):
        order_confirmation = self.oanda.create_order(self.account_id,
                                                 instrument=order.instrument,
                                                 units=order.units,
                                                 side=order.side,
                                                 type=order.type,
                                                 price=order.price,
                                                 expiry=order.expiry
                                                 )

        return order_confirmation

    @property
    def account_id(self):
        return os.environ['OANDA_ACCOUNT_ID']

    @property
    def oanda(self):
        import oandapy

        if self._oanda is None:
            self._oanda = oandapy.API(environment=os.environ['OANDA_ENV'], access_token=os.environ['OANDA_ACCESS_TOKEN'])
        return self._oanda

