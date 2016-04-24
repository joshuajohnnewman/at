from trading.algorithms.random_stumps import RandomStumps
from trading.broker.oanda import OandaBroker
from trading.live_trading.base import LiveTradingStrategy
from trading.algorithms.constants import INSTRUMENT_EUR_USD


def main():
    classifier_id = '571bf11f16890198e1e0243d'
    strategy_id = None

    broker = OandaBroker()
    pair_a =  {'name': 'usd', 'amount': 1000}
    pair_b = {'name': 'eur', 'amount': 0}

    instrument = INSTRUMENT_EUR_USD
    classifier_config = {'classifier_id': classifier_id}

    strategy_config = {
        'instrument': instrument,
        'pair_a': pair_a,
        'pair_b': pair_b,
        'classifier_config': classifier_config
    }


    random_stumps_strategy = RandomStumps(strategy_config, strategy_id)

    strategy = LiveTradingStrategy(random_stumps_strategy, broker)
    strategy.tick()


if __name__ == '__main__':
    main()