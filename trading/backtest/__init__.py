import json


def get_historical_data(file):
    with open(file) as f:
        data = json.load(file)
    return data