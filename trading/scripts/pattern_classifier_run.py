from trading.algorithms.simple_pattern_matcher import PatternMatch
from trading.broker.oanda import OandaBroker
from trading.live_trading.base import LiveTradingStrategy
from trading.algorithms.constants import INSTRUMENT_EUR_USD


def main():
    classifier_id = '5743335b7f9b5ebdf9d84827'

    broker = OandaBroker()
    pair_a =  {'name': 'usd', 'starting_currency': 1000, 'tradeable_currency': 1000}
    pair_b = {'name': 'eur', 'starting_currency': 0, 'tradeable_currency': 0}

    instrument = INSTRUMENT_EUR_USD
    classifier_config = {'classifier_id': classifier_id}

    strategy_config = {
        'instrument': instrument,
        'pair_a': pair_a,
        'pair_b': pair_b,
        'classifier_config': classifier_config
    }

    pattern_match_strategy = PatternMatch(strategy_config)

    strategy = LiveTradingStrategy(pattern_match_strategy, broker)
    strategy.tick()


if __name__ == '__main__':
    main()
