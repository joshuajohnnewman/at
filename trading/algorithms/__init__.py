ORDER_SELL = 'sell'
ORDER_BUY = 'buy'
ORDER_STAY = 'stay'


from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.algorithms.moving_average_crossover import MAC
from trading.algorithms.random_stumps import RandomStumps
from trading.algorithms.simple_pattern_matcher import PatternMatch


STRATEGIES = {
    PatternMatch.name: PatternMatch,
    Josh.name: Josh,
    MAC.name: MAC,
    RandomStumps.name: RandomStumps
}


def initialize_strategy(strategy_config, account_information):
    strategy_name = strategy_config['strategy_name']
    base_pair_balance = account_information['balance']
    base_pair_currency = account_information['accountCurrency']
    base_pair = strategy_config['base_pair']
    base_pair['starting_units'] = base_pair_balance
    base_pair['tradeable_units'] = base_pair_balance

    print(base_pair_currency, base_pair['currency'])
    assert(base_pair_currency.lower() == base_pair['currency'].lower())

    strategy = STRATEGIES[strategy_name](strategy_config)

    return strategy
