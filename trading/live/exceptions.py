KeyboardInterruptMessage = 'manually stopped strategy'


class LiveTradingException(Exception):
    """
    Base class for live trading errors.
    """
    pass


class BrokerException(LiveTradingException):
    """
    Broker Error.
    """
    message = 'Broker Error.'


class StrategyException(LiveTradingException):
    """
    Insufficient score
    """
    MESSAGE_FORMAT = 'Trading strategy exception'

    def __init__(self, update_id, score, category, threshold):
        self.message = self.MESSAGE_FORMAT.format(uid=update_id, threshold=threshold, category=category, score=score)


class ClassifierException(LiveTradingException):
    """
    Classifier Exception
    """
    MESSAGE_FORMAT = 'Classifier exception.'

    def __init__(self, update_id, score, category, threshold):
        self.message = self.MESSAGE_FORMAT.format(uid=update_id, threshold=threshold, category=category, score=score)
