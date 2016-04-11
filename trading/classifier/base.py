from abc import abstractmethod, ABCMeta


class Classifier:
    __metaclass__ = ABCMeta

    def passes_filter(self, datum):
        return True

    @abstractmethod
    def load_serialized_classifier(self, serialized_classifier):
        raise NotImplementedError

    @abstractmethod
    def serialize_classifier(self):
        raise NotImplementedError

    @abstractmethod
    def prepare_prediction_data(self, data):
        raise NotImplementedError

    @abstractmethod
    def prepare_training_data(self, data):
        raise NotImplementedError