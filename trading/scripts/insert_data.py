import json

import time
from bson import ObjectId
from argparse import ArgumentParser
from trading.db import get_database

DATE_FORMAT = 'YYYY-M-D-H-m'


def load_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def _get_default_chart(instrument, granularity, title):
    chart_data = {
        'granularity': granularity,
        'instrument': instrument,
        'x_params': {
            'interval': 1,
            'valueFormatString': DATE_FORMAT
        },
        'y_params': {
            'includeZero': False,
            'prefix': '$',
            'title': 'Prices'
        },
        'title': {
            'text': title
        },
        'candles': ''
    }
    return chart_data


def main(input_file, instrument, granularity, title):
    db = get_database()
    candle_data = load_json(input_file)

    chart = _get_default_chart(instrument, granularity, title)

    candle_size = len(candle_data)

    max_candle_slice = 30000
    print(max_candle_slice, candle_size)
    if candle_size < max_candle_slice:
        chart['candles'] = candle_data
        db.candle_data.insert(chart)
    else:
        target_num_pieces = (candle_size / max_candle_slice) + 1
        for i in range(0, target_num_pieces):
            start_slice = max_candle_slice * i
            end_slice = start_slice + max_candle_slice
            chart['candles'] = candle_data[start_slice:end_slice]
            old_title = chart['title']['text']
            chart['title']['text'] = old_title + '_' + str(i)
            time.sleep(2)
            chart['_id'] = ObjectId()
            print('Start:', start_slice, 'End:', end_slice)
            db.candle_data.insert(chart)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('instrument')
    parser.add_argument('granularity')
    parser.add_argument('title')
    args = parser.parse_args()

    main(args.input_file, args.instrument, args.granularity, args.title)
