import logging
import os

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_restful import Api
from werkzeug.contrib.cache import SimpleCache

from trading.api import ok

from trading.api.classifiers import Classifiers
from trading.util.log import configure_logging
from trading.trading_auth.auth import authorize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('trading-api-{env}'.format(env=os.environ['ENVIRONMENT']))
logger = configure_logging(logger)


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
    configure_logging(application.logger)
    application.run()
