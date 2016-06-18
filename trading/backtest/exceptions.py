

class BacktestException(Exception):
    """
    Base class for backtest errors.
    """
    pass


class BacktestBrokerException(BacktestException):
    """
    Broker Error.
    """
    message = 'Backtest Broker Error.'


class BacktestStrategyException(BacktestException):
    """
    Insufficient score
    """
    MESSAGE_FORMAT = 'Backtest Trading strategy exception'

    def __init__(self, update_id, score, category, threshold):
        self.message = self.MESSAGE_FORMAT.format(uid=update_id, threshold=threshold, category=category, score=score)


class BacktestClassifierException(BacktestException):
    """
    Classifier Exception
    """
    MESSAGE_FORMAT = 'Backtest Classifier exception.'

    def __init__(self, update_id, score, category, threshold):
        self.message = self.MESSAGE_FORMAT.format(uid=update_id, threshold=threshold, category=category, score=score)
