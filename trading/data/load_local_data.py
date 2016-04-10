import json

from trading.util.data import get_data_path


def load_json(file_name):
    file_path = get_data_path(file_name)
    with open(file_path) as f:
        data = json.load(f)
    return data
