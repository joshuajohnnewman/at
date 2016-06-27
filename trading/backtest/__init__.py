import json


def get_historical_data(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data
