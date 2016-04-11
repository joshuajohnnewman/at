from flask_restful import Resource

from trading.api import ok
from trading.db import get_database


class Brokers(Resource):
    def get(self):
        print('Brokers ENDPOINT')
        db = get_database()
        strategies = list(db.brokers.find({}))

        return {'live_strategies': strategies}

    def post(self):
        return ok()
