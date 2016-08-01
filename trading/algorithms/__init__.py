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

CLASSIFIER_STRATEGIES = {(PatternMatch.name, RandomStumps.name)}


def initialize_strategy(account_information, strategy_name, instrument=None, base_pair=None, quote_pair=None,
                        classifier_id=None, strategy_id=None):

    #  Update base pair data from broker account
    base_pair_balance = account_information['balance']
    base_pair_currency = account_information['accountCurrency']
    base_pair['starting_units'] = base_pair_balance
    base_pair['tradeable_units'] = base_pair_balance

    assert(base_pair_currency.lower() == base_pair['currency'].lower())

    if strategy_name in CLASSIFIER_STRATEGIES:
        strategy = STRATEGIES[strategy_name](strategy_id, instrument, base_pair, quote_pair, classifier_id)
    else:
        strategy = STRATEGIES[strategy_name](strategy_id, base_pair, quote_pair)

    return strategy
