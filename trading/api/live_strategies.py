from bson import ObjectId
from flask import request
from flask_restful import Resource

from trading.api import ok
from trading.db import get_database
from trading.live_trading import initialize_live_strategy


class LiveStrategies(Resource):
    def get(self):
        print('LIVE STRATEGIES ENDPOINT')
        db = get_database()
        live_strategies = list(db.live_strategies.find({}))

        return {'live_strategies': live_strategies}

    def post(self):
        live_strategy_id = request.get('live_strategy_id')
        db = get_database()
        strategy = db.live_strategies.findOne({'_id': ObjectId(live_strategy_id)})

        live_strategy = initialize_live_strategy(db, strategy)

        live_strategy.tick()

        return ok()
