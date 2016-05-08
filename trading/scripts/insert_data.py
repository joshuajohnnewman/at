import json


from argparse import ArgumentParser

from trading.db import get_database


def load_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    num_candles = len(data)
    return data[0: num_candles/12]


def _get_default_chart():
    chart_data = {
        "x_params": {
            "interval": 1,
            "valueFormatString": "YYYY-M-D-H"
        },
        "y_params": {
            "includeZero": False,
            "prefix": "$",
            "title": "Prices"
        },
        "title": {
            "text": "Citrix Systems Stock Prices for May 2014"
        },
        "candles": ''
    }
    return chart_data


def main(input_file):
    db = get_database()
    candle_data = load_json(input_file)

    chart = _get_default_chart()
    chart['candles'] = candle_data

    db.candle_data.insert(chart)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input_file')
    args = parser.parse_args()

    main(args.input_file)
