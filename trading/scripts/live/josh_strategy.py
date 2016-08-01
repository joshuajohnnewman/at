from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.broker.oanda import OandaBroker
from trading.live.live_runner import LiveTradingStrategyRunner


def main():
    strategy_id = '571d2ec21689011340cce43f'

    base_pair = {'currency': 'usd'}
    quote_pair = {'currency': 'eur'}
    instrument = INSTRUMENT_EUR_USD
    broker = OandaBroker(instrument)

    strategy_name = Josh.name

    if strategy_id is None:
        strategy = LiveTradingStrategyRunner(broker, instrument, strategy_name, base_pair, quote_pair)
    else:
        strategy = LiveTradingStrategyRunner(broker, instrument, strategy_name, base_pair, quote_pair, strategy_id)

    strategy.tick()


if __name__ == '__main__':
    main()
