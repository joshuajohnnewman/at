from abc import abstractmethod, ABCMeta
from collections import namedtuple

Order = namedtuple('Order', ('instrument', 'units', 'side', 'type', 'price', 'expiry'))


class Broker(object):
    __metaclass__ = ABCMeta

    def __init__(self, instrument):
        self.instrument = instrument

    @abstractmethod
    def get_account_information(self):
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id):
        raise NotImplementedError

    @abstractmethod
    def make_order(self, order):
        raise NotImplementedError

    @abstractmethod
    def get_current_price_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_historical_price_data(self, count, granularity):
        raise NotImplementedError
