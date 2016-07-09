from flask_restful import Resource

from trading.db import get_database, transform_son


class Strategies(Resource):
    def get(self):
        print('STRATEGIES ENDPOINT')
        db = get_database()
        query = {}
        strategies = list(db.strategies.find(query))

        strategies = map(transform_son, strategies)

        return {'strategies': strategies}
