from trading.algorithms import initialize_strategy
from trading.broker import initialize_broker
from trading.live_trading.base import LiveTradingStrategy


def initialize_live_strategy(serialized_live_strategy, db):
    broker_name = serialized_live_strategy['broker']
    strategy_id = serialized_live_strategy['strategy_id']


