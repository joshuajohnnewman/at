import datetime
import json
import random
import time

from argparse import ArgumentParser


from trading.db import get_database

epoch = datetime.datetime(1970,1,1)


def make_candle_data(start, granularity,  num_candles):
    candles = []
    datetimes = []

    ndt = start
    for i in range(0, num_candles):
        if granularity == 'h':
            ndt = ndt + datetime.timedelta(hours=1)
        elif granularity == 'd':
            ndt = ndt + datetime.timedelta(hours=1)
        datetimes.append(ndt)


    for i, dt in enumerate(datetimes):
        candle = {
            'high': random.uniform(40, 100),
            'low': random.uniform(40, 100),
            'close': random.uniform(40, 100),
            'open': random.uniform(40, 100)
        }

        date = {
            'year': dt.year,
            'month': dt.month,
            'day': dt.day,
            'hour': dt.hour,
            'utc': (dt - epoch).total_seconds()
        }
        candles.append({
            'candle': candle,
            'date': date,
            'id': time.time()
        })
    return candles

chart_data = {
    "x_params" : {
		"interval" : 1,
		"valueFormatString" : "YYYY-M-D-H"
	},
    "y_params" : {
		"includeZero" : False,
		"prefix" : "$",
		"title" : "Prices"
	},
    "title": {
        "text": "Citrix Systems Stock Prices for May 2014"
    },
    "candles": ''
}


def dump_file(cd):
    with open('output_chart.json') as f:
        json.dump(cd, f)


def main(yr, month, day, granularity, num_candles):
    start = datetime.datetime.utcnow()
    candles = make_candle_data(start, granularity, int(num_candles))
    chart_data['candles'] = candles
    print('Chart Data', chart_data)
    db = get_database()
    db.candle_data.insert(chart_data)



if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('start_year')
    arg_parser.add_argument('start_month')
    arg_parser.add_argument('start_day')
    arg_parser.add_argument('granularity')
    arg_parser.add_argument('num_candles')

    args = arg_parser.parse_args()
    main(args.start_year, args.start_month, args.start_day, args.granularity, args.num_candles)