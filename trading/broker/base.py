from abc import abstractmethod, ABCMeta
from collections import namedtuple

Order = namedtuple('Order', ('instrument', 'units', 'side', 'type', 'price', 'expiry'))

class Broker(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def make_order(self, order):
        raise NotImplementedError

    @abstractmethod
    def get_current_price_data(self, instrument):
        raise NotImplementedError

    def get_historical_price_data(self, instrument, count=30, granularity='D'):
        raise NotImplementedError
