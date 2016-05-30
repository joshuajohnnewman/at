from trading.algorithms.simple_pattern_matcher import PatternMatch
from trading.broker.oanda import OandaBroker
from trading.live_trading.base import LiveTradingStrategy
from trading.algorithms.constants import INSTRUMENT_EUR_USD


def main():
    classifier_id = '5743335b7f9b5ebdf9d84827'

    broker = OandaBroker()
    base_pair =  {'currency': 'usd'}
    quote_pair = {'currency': 'eur'}

    instrument = INSTRUMENT_EUR_USD
    classifier_config = {'classifier_id': classifier_id}

    strategy_config = {
        'strategy_name': PatternMatch.name,
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair,
        'classifier_config': classifier_config
    }

    strategy = LiveTradingStrategy(strategy_config, broker)
    strategy.tick()


if __name__ == '__main__':
    main()
