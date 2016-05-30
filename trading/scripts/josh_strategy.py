from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.broker.oanda import OandaBroker
from trading.live_trading.base import LiveTradingStrategy
from trading.algorithms.constants import INSTRUMENT_EUR_USD


def main():
    broker = OandaBroker()
    strategy_id = '571d2ec21689011340cce43f'

    base_pair =  {'currency': 'usd', 'starting_units': 1000, 'tradeable_units': 1000}
    quote_pair = {'currency': 'eur', 'starting_units': 0, 'tradeable_units': 0}
    instrument = INSTRUMENT_EUR_USD

    config = {
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair
    }

    id_config = {
        'strategy_id': strategy_id
    }

    josh_strategy = Josh(config)

    strategy = LiveTradingStrategy(josh_strategy, broker)
    strategy.tick()


if __name__ == '__main__':
    main()