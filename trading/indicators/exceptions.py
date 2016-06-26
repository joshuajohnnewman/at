

class IndicatorException(Exception):
    """
    Base class for indicator calculation errors.
    """
    pass


class TalibIntervalException(IndicatorException):
    """
    Talib Interval Range Error.
    """
    message = 'Interval Range Error.'
