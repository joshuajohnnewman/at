from flask_restful import Resource

from trading.db import get_database, transform_son


class Classifiers(Resource):
    def get(self):
        db = get_database()
        query = {}
        projection = {'classifier': False}
        classifiers = transform_son(db.classifiers.find_one(query, projection))

        return {'classifiers': classifiers}
