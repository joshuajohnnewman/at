from trading.algorithms.random_stumps import RandomStumps
from trading.broker.oanda import OandaBroker
from trading.live_trading.base import LiveTradingStrategy
from trading.algorithms.constants import INSTRUMENT_EUR_USD


def main():
    classifier_id = '571bf11f16890198e1e0243d'

    broker = OandaBroker()
    base_pair =  {'currency': 'usd', 'starting_units': 1000, 'tradeable_units': 1000}
    quote_pair = {'currency': 'eur', 'starting_units': 0, 'tradeable_units': 0}

    instrument = INSTRUMENT_EUR_USD
    classifier_config = {'classifier_id': classifier_id}

    strategy_config = {
        'stragegy_name': RandomStumps.name,
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair,
        'classifier_config': classifier_config
    }


    random_stumps_strategy = RandomStumps(strategy_config)

    strategy = LiveTradingStrategy(random_stumps_strategy, broker)
    strategy.tick()


if __name__ == '__main__':
    main()