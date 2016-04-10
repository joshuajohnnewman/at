import os

from requests import Session


def get_trading_api_session(ssl_auth=True):
    session = Session()
    headers = {'User-Agent': 'trading'}
    if ssl_auth:
        headers.update({'X-SSL-AUTH': os.environ['TRADING_API_CERT']})
    session.headers.update(headers)
    return session