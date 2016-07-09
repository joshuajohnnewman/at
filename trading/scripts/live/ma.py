from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.algorithms.moving_average_crossover import MAC
from trading.broker.oanda import OandaBroker
from trading.live.live_runner import LiveTradingStrategyRunner


def main():
    strategy_id = '571d2ec21689011340cce43f'

    base_pair = {'currency': 'usd', 'starting_units': 1000}
    quote_pair = {'currency': 'eur', 'starting_units': 0}
    instrument = INSTRUMENT_EUR_USD
    broker = OandaBroker(instrument)

    config = {
        'strategy_name': MAC.name,
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
