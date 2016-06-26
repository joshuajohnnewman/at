from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.backtest.backtest_oanda_broker import BacktestBroker
from trading.backtest.base import BacktestTradingStrategy


def main():

    base_pair =  {'currency': 'usd', 'starting_units': 1000}
    quote_pair = {'currency': 'eur', 'starting_units': 0}
    instrument = INSTRUMENT_EUR_USD
    backtest_length = 5000
    broker = BacktestBroker(instrument, base_pair, quote_pair)

    config = {
        'strategy_name': Josh.name,
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair
    }

    strategy = BacktestTradingStrategy(config, broker, backtest_length)
    strategy.tick()


if __name__ == '__main__':
    main()