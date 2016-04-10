import os

from werkzeug.exceptions import abort

from trading.config import DEBUG


ROUTE_AUTH = 'https://internal-auth.trading.com/api/users/me'


def authorize(request):
    token = _get_token(request)
    if token == os.environ['AUTH_TOKEN']:
        return True
    else:
        abort(401)

def _get_token(request):
    token = request.headers.get('X-Trading-Auth-Token')
    if DEBUG and not token:
        return os.getenv('DEBUG_TOKEN')
    return token


def _get_token_cache_key(token):
    return 'auth:' + token
