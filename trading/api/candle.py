import logging
import sys
import traceback

from bson import ObjectId
from flask import request
from flask_restful import Resource

from trading.api import ok, abort
from trading.api.util import find_chart_start_end_date, find_marked_candles, find_target_candle, make_date_id_map
from trading.db import get_database, transform_son

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class Candle(Resource):
    def get(self):
        logging.info('At Candle GET Endpoint')
        try:
            db = get_database()

            chart_id = request.query_string.split('=')[1]
            chart_data = transform_son(db.candle_data.find_one({'_id': ObjectId(chart_id)}))
            title = chart_data['title']
            y_params = chart_data['y_params']
            x_params = chart_data['x_params']
            candles = chart_data['candles']
        except Exception as e:
            logging.info('E %s', e)
            traceback.print_exc(file=sys.stdout)
            return abort(status=500)

        return {'candles': candles, 'chart_id': chart_data['id'], 'title': title, 'y_params': y_params,
                'x_params': x_params}

    def post(self):
        logging.info('At Candle POST Endpoint')
        request_data = request.get_json()
        candle = request_data.get('candle')
        pattern = request_data.get('pattern')
        hours_offset = request_data.get('hours_offset')
        chart_id = request_data.get('chart_id')

        db = get_database()

        try:
            chart_id = ObjectId(chart_id)
            chart_data = transform_son(db.candle_data.find_one({'_id': chart_id}))
            date_id_map = make_date_id_map(chart_data['candles'], hours_offset)
            target_candle = find_target_candle(candle, date_id_map)
            target_candle_id = target_candle['id']

            target_candle['pattern'] = pattern
            query = {'_id': chart_id, 'candles.id': target_candle_id}
            update = {'$set': {'candles.$': target_candle}}

            print(query, update)
            db.candle_data.update(query, update)

        except Exception as e:
            logging.error('E %s', e)
            traceback.print_exc(file=sys.stdout)
            return abort(status=500)

        return ok(202)


class CandleCharts(Resource):
    def get(self):
        logging.info('AT CandleCharts GET Endpoint')
        db = get_database()
        charts = db.candle_data.find()
        charts = map(transform_son, charts)

        chart_data = {}

        try:
            for chart in charts:
                chart_id = chart['id']
                granularity = chart['granularity']
                candles = chart['candles']
                instrument = chart['instrument']
                start_date, end_date = find_chart_start_end_date(candles)

                num_candles = len(candles)
                chart_data[chart_id] = {
                    'instrument': instrument,
                    'granularity': granularity,
                    'num_candles': num_candles,
                    'start_date': start_date,
                    'end_date': end_date
                }
        except Exception as e:
            logging.error('E %s', e)
            traceback.print_exc(file=sys.stdout)
            return abort(status=500)

        return {'charts': chart_data}


class CandlePattern(Resource):
    def get(self):
        logging.info('At CandlePattern GET Endpoint')
        db = get_database()
        charts = db.candle_data.find()
        charts = map(transform_son, charts)

        marked_candles = find_marked_candles(charts)

        return {'candles': marked_candles}
