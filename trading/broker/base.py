from abc import abstractmethod, ABCMeta
from collections import namedtuple

Order = namedtuple('Order', ('instrument', 'units', 'side', 'type', 'price', 'expiry'))


class Broker:
    __metaclass__ = ABCMeta

    @abstractmethod
    def make_order(self, order):
        raise NotImplementedError

    @abstractmethod
    def get_price_data(self, instrument):
        raise NotImplementedError