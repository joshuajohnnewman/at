ORDER_SELL = 'sell'
ORDER_BUY = 'buy'
ORDER_STAY = 'stay'


from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.algorithms.moving_average_crossover import MAC
from trading.algorithms.random_stumps import RandomStumps


STRATEGIES = {
    Josh.name: Josh,
    MAC.name: MAC,
    RandomStumps.name: RandomStumps
}


def initialize_strategy(serialized_strategy):
    target_strategy = serialized_strategy['strategy_name']
    instrument = serialized_strategy['instrument']
    pair_a = serialized_strategy['pair_a']
    pair_b = serialized_strategy['pair_b']

    strategy = target_strategy(instrument, pair_a, pair_b)

    return strategy
