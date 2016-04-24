from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_restful import Api
from werkzeug.contrib.cache import SimpleCache

from trading.api import ok

from trading.api.classifiers import Classifiers
from trading.api.strategies import Strategies
from trading.trading_auth.auth import authorize
from trading.util.log import Logger

logger = Logger()


class TradingApi(Api):
    def handle_error(self, e):
        logger.error(e, exc_info=True)
        code = getattr(e, 'code', 500)
        if code == 500:
            return self.make_response({'errors': [str(e)]}, 500)
        return super(TradingApi, self).handle_error(e)  # Non 500 errors


UNAUTHENTICATED_ENDPOINTS = {'/status'}
UNAUTHENTICATED_METHODS = {'OPTIONS'}

application = Flask(__name__)
application.debug = 'DEBUG'

cache = SimpleCache()

cors = CORS(application)

api = TradingApi(application, prefix='/api/v1')
api.add_resource(Classifiers, '/classifiers')
api.add_resource(Strategies, '/strategies')

@application.before_request
def before_request():
    if request.path not in UNAUTHENTICATED_ENDPOINTS and request.method not in UNAUTHENTICATED_METHODS:
        authorize(request)


@application.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.client.close()


@application.route('/status')
def status():
    return jsonify(ok()[0])


if __name__ == '__main__':
    application.run()
