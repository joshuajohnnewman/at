from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api
from werkzeug.contrib.cache import SimpleCache

from trading.api import ok

from trading.api.candle import Candle
from trading.api.classifiers import Classifiers
from trading.api.strategies import Strategies
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

api = TradingApi(application, prefix='/api/v1')
api.add_resource(Candle, '/candle')
api.add_resource(Classifiers, '/classifiers')
api.add_resource(Strategies, '/strategies')


CORS(application)



@application.route('/status')
def status():
    return jsonify(ok()[0])


if __name__ == '__main__':
    from flask import url_for
    with application.test_request_context():
        print url_for('candle')
    application.run()
