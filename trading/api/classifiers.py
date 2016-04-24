from flask_restful import Resource

from trading.db import get_database, transform_son


class Classifiers(Resource):
    def get(self):
        print('OBJECTIVE CLASSIFIER ENDPOINT')
        db = get_database()
        print('db', db)
        classifiers = transform_son(db.classifiers.find_one({}))
        print(classifiers)

        return {'classifiers': classifiers}
