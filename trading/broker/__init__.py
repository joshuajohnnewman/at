from collections import namedtuple

from trading.broker.oanda import OandaBroker

MarketOrder = namedtuple('MarketOrder', ('instrument', 'units', 'side', 'type', 'price', 'expiry'))


BROKERS = {
    OandaBroker.name: OandaBroker
}


def initialize_broker(serialized_broker):
    broker_name = serialized_broker['name']
    broker = BROKERS[broker_name]()
    return broker
