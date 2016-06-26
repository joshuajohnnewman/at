from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.broker.oanda import OandaBroker
from trading.live.live_runner import LiveTradingStrategyRunner


def main():
    broker = OandaBroker()
    strategy_id = '571d2ec21689011340cce43f'

    base_pair =  {'currency': 'usd'}
    quote_pair = {'currency': 'eur'}
    instrument = INSTRUMENT_EUR_USD

    config = {
        'strategy_name': Josh.name,
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair
    }

    id_config = {
        'strategy_id': strategy_id
    }

    strategy = LiveTradingStrategyRunner(config, broker)
    strategy.tick()


if __name__ == '__main__':
    main()