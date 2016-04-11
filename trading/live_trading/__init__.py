from trading.broker import initialize_broker
from trading.algorithms import initialize_strategy
from trading.live_trading.base import LiveTradingStrategy


def initialize_live_strategy(db, serialized_live_strategy):
    strategy_id = serialized_live_strategy['strategy_id']
    serialized_strategy = db.strategies.find_one({'_id': strategy_id})
    strategy = initialize_strategy(serialized_strategy)

    broker_id = serialized_live_strategy['broker_id']
    serialized_broker = db.brokers.find_one({'_id': broker_id})
    broker = initialize_broker(serialized_broker)

    live_strategy = LiveTradingStrategy(strategy, broker)

    return live_strategy