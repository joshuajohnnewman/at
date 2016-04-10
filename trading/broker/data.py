

def get_prices(broker, instrument):
    broker_response = broker.get_prices(instruments=instrument)
    return broker_response
