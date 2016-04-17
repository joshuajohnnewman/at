from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.broker.oanda import OandaBroker
from trading.live_trading.base import LiveTradingStrategy
from trading.algorithms.constants import INSTRUMENT_EUR_USD


def main():
    broker = OandaBroker()

    pair_a =  {'name': 'usd', 'amount': 1000}
    pair_b = {'name': 'eur', 'amount': 0}

    instrument = INSTRUMENT_EUR_USD

    josh_strategy = Josh(instrument, pair_a, pair_b)

    strategy = LiveTradingStrategy(josh_strategy, broker)
    strategy.tick()


if __name__ == '__main__':
    main()