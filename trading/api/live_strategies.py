from bson import ObjectId
from flask import request
from flask_restful import Resource

from trading.api import ok
from trading.db import get_database
from trading.broker import initialize_broker
from trading.algorithms import initialize_strategy
from trading.live_trading.base import LiveTradingStrategy


def initialize_live_strategy(db, serialized_live_strategy):
    strategy_id = serialized_live_strategy['strategy_id']
    serialized_strategy = db.strategies.find_one({'_id': strategy_id})
    strategy = initialize_strategy(serialized_strategy)

    broker_id = serialized_live_strategy['broker_id']
    serialized_broker = db.brokers.find_one({'_id': broker_id})
    broker = initialize_broker(serialized_broker)

    live_strategy = LiveTradingStrategy(strategy, broker)

    live_strategy.tick()


class LiveStrategies(Resource):
    def get(self):
        print('LIVE STRATEGIES ENDPOINT')
        db = get_database()
        strategies = list(db.live_strategies.find({}))

        return {'strategies': strategies}

    def post(self):
        live_strategy_id = request.get('live_strategy_id')
        db = get_database()
        strategy = db.live_strategies.findOne({'_id': ObjectId(live_strategy_id)})


        live_strategy = initialize_live_strategy(db, strategy)

        live_strategy.tick()

        return ok()
