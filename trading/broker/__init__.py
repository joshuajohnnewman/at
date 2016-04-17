from collections import namedtuple

from trading.broker.oanda import OandaBroker

MarketOrder = namedtuple('MarketOrder', ('instrument', 'units', 'side', 'type', 'price', 'expiry'))

OANDA = 'oanda'

SIDE_BUY = 'buy'
SIDE_SELL = 'sell'
SIDE_STAY = 'stay'

ORDER_LIMIT = 'limit'
ORDER_STOP = 'stop'
ORDER_MARKET = 'market'

BROKERS = {
    OANDA: OandaBroker
}

def initialize_broker(serialized_broker):
    broker_name = serialized_broker['name']
    broker = BROKERS[broker_name]()
    return broker