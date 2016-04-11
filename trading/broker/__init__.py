from trading.broker.oanda import OandaBroker

OANDA = 'oanda'

BROKERS = {
    OANDA: OandaBroker
}

def initialize_broker(serialized_broker):
    broker_name = serialized_broker['name']
    broker = BROKERS[broker_name]()
    return broker