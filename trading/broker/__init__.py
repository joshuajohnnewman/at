from collections import namedtuple

from trading.broker.oanda import OandaBroker

MarketOrder = namedtuple('MarketOrder', ('instrument', 'units', 'side', 'type', 'price', 'expiry'))

OANDA = 'oanda'

SIDE_BUY = 'buy'
SIDE_SELL = 'sell'

BROKERS = {
    OANDA: OandaBroker
}

def initialize_broker(serialized_broker):
    broker_name = serialized_broker['name']
    broker = BROKERS[broker_name]()
    return broker