from flask_restful import Resource

from trading.api import abort
from trading.db import get_database


class Classifiers(Resource):
    def get(self):
        print('OBJECTIVE CLASSIFIER ENDPOINT')
        db = get_database()
        classifiers = list(db.classifiers.find({}))

        return {'classifiers': classifiers}
