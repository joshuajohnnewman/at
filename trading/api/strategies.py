from flask_restful import Resource

from trading.api import ok
from trading.db import get_database


class Strategies(Resource):
    def get(self):
        print('STRATEGIES ENDPOINT')
        db = get_database()
        strategies = list(db.strategies.find({}))

        return {'live_strategies': strategies}

    def post(self):
        return ok()
