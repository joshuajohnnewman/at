from bson import ObjectId
from flask import request
from flask_restful import Resource

from trading.api import ok
from trading.db import get_database, transform_son
from trading.live import initialize_live_strategy


class LiveStrategies(Resource):
    def get(self):
        print('LIVE STRATEGIES ENDPOINT')
        db = get_database()
        live_strategies = list(db.live_strategies.find({}))
        live_strategies = map(transform_son, live_strategies)

        return {'live_strategies': live_strategies}

    def post(self):
        live_strategy_id = request.get('live_strategy_id')
        db = get_database()
        strategy = db.live_strategies.findOne({'_id': ObjectId(live_strategy_id)})

        print('Initializing live strategy...')
        live_strategy = initialize_live_strategy(db, strategy)

        print('Starting tick loop...')
        live_strategy.tick()

        return ok()
