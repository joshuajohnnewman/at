import json



def get_training_data(broker, instrument, count, granularity):
    broker_response = broker.get_historical_price_data(instrument, count=count, granularity=granularity)
    return broker_response


def transform_training_data(data):
    pass

def get_local_data(file):
    with open(file) as f:
        data = json.load(f)
    return data
