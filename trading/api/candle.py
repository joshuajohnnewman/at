from bson import ObjectId
from flask import request
from flask_restful import Resource

from trading.api import ok
from trading.db import get_database, transform_son


def is_matching_date(a, b):
    print('a', a)
    print('b', b)
    return a['year'] == b['year'] and a['month'] == b['month'] and a['day'] == b['day']


def _find_target_candle(target_candle, candles):
    target_date = target_candle['date']
    matching_candle = None
    try:
        matching_candle = [candle for candle in candles if is_matching_date(candle['date'], target_date)][0]
    except IndexError as e:
        print('No matching candle', e)
    return matching_candle


date_map = {
    'Feb': 2
}


def format_candle(candle):
    date_parts = candle['date'].split('-')
    print(date_parts)
    month = date_map[date_parts[0]]
    day = date_parts[1]
    high = candle['high']
    low = candle['low']
    close = candle['close']
    open = candle['open']
    return {
        'date': {
            'year': 2015,
            'month': month,
            'day': int(day)
        },
        'candle': {
            'high': high[high.index(':'):],
            'low': low[low.index(':'):],
            'close': close[close.index(':'):],
            'open': open[open.index(':'):]
        }
    }

class Candle(Resource):
    def get(self):
        print('At Candle GET Endpoint')
        query_string = request.query_string
        print(query_string)

        db = get_database()
        chart_data = transform_son(db.candle_data.find_one())
        print(chart_data)
        title = chart_data['title']
        y_params = chart_data['y_params']
        x_params = chart_data['x_params']
        candles = chart_data['candles']

        return {'candles': candles, 'title': title, 'y_params': y_params, 'x_params': x_params}


    def post(self):
        print('At Candle POST Endpoint')
        request_data = request.get_json()
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        granularity = request_data.get('granularity')
        candle = request_data.get('candle')
        pattern = request_data.get('pattern')

        candle = format_candle(candle)
        """
        db = get_database()
        chart_data = transform_son(db.candle_data.find_one())

        target_candle = _find_target_candle(candle, chart_data['candles'])
        target_candle_id = target_candle['id']

        query = {'_id': ObjectId(chart_data['id']), 'candles.id': target_candle_id}

        update = {'$set': {'candles.$', candle}}

        db.candle_data.update(query, update)
        """

        print(start_date, end_date, granularity, candle, pattern)

        return ok(202)