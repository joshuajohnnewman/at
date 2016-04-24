from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.broker.oanda import OandaBroker
from trading.live_trading.base import LiveTradingStrategy
from trading.algorithms.constants import INSTRUMENT_EUR_USD


def main():
    broker = OandaBroker()

    pair_a =  {'name': 'usd', 'starting_currency': 1000, 'tradeable_currency': 1000}
    pair_b = {'name': 'eur', 'starting_currency': 0, 'tradeable_currency': 0}
    strategy_id = '571d2ec21689011340cce43f'
    instrument = INSTRUMENT_EUR_USD

    config = {
        'instrument': instrument,
        'pair_a': pair_a,
        'pair_b': pair_b
    }

    id_config = {
        'strategy_id': strategy_id
    }
    josh_strategy = Josh(id_config)

    strategy = LiveTradingStrategy(josh_strategy, broker)
    strategy.tick()


if __name__ == '__main__':
    main()