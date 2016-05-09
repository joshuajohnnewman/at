import json


from argparse import ArgumentParser

from trading.db import get_database


def load_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def _get_default_chart(instrument, granularity, title):
    chart_data = {
        "granularity": granularity,
        "instrument": instrument,
        "x_params": {
            "interval": 1,
            "valueFormatString": "YYYY-M-D-H-m"
        },
        "y_params": {
            "includeZero": False,
            "prefix": "$",
            "title": "Prices"
        },
        "title": {
            "text": title
        },
        "candles": ''
    }
    return chart_data


def main(input_file, instrument, granularity, title):
    db = get_database()
    candle_data = load_json(input_file)

    chart = _get_default_chart(instrument, granularity, title)

    candle_size = len(candle_data)

    max_candle_slice = 30000
    if candle_size > max_candle_slice:
        chart['candles'] = candle_data
        db.candle_data.insert(chart)
    else:
        target_num_pieces = (candle_size / max_candle_slice) + 1
        for i in range(0, target_num_pieces):
            start_slice = max_candle_slice * i
            end_slice = start_slice + max_candle_slice
            chart['candles'] = candle_data[start_slice:end_slice]
            db.candle_data.insert(chart)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('instrument')
    parser.add_argument('granularity')
    parser.add_argument('title')
    args = parser.parse_args()

    main(args.input_file, args.instrument, args.granularity, args.title)
