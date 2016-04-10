import pickle as pkl

from sklearn import ensemble

from trading.classifier.base import Classifier
from trading.util.log import Logger


class RFClassifier(Classifier):

    NUM_ESTIMATORS = 10

    _classifier = None
    _training_data = None


    def predict(self, X, format_data, unwrap_prediction=False):
        if format_data is True:
            X = self.prepare_prediction_data(X)
        prediction = self.classifier.predict(X)

        if unwrap_prediction is True:
            prediction = prediction[0]

        return prediction

    def train(self):
        X, y = self.prepare_training_data()
        self.classifier.fit(X,y)

    def generate_training_data(self, num_periods):
        pass

    def remove_training_data(self):
        pass

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = ensemble.RandomForestClassifier(n_estimators=self.NUM_ESTIMATORS)
        return self._classifier

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger
