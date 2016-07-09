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
    Strategy Error
    """
    MESSAGE_FORMAT = 'Trading strategy exception'


class ClassifierException(LiveTradingException):
    """
    Classifier Error
    """
    MESSAGE_FORMAT = 'Classifier exception.'
