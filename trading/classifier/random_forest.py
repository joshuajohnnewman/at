import pickle as pkl

from bson import ObjectId
from sklearn import ensemble

from trading.classifier.base import Classifier, MarketPrediction, predictions_map
from trading.trading_constants import STRATEGY_DECISION


class RFClassifier(Classifier):

    NUM_ESTIMATORS = 10

    _training_data = None

    def __init__(self, config):
        classifier_id = config['classifier_id']

        if classifier_id is None:
            classifier_id = ObjectId()
            self.classifier = ensemble.RandomForestClassifier(n_estimators=self.NUM_ESTIMATORS)
        else:
            classifier = self.db.find_one({'_id': ObjectId(classifier_id)})
            self.classifier = self.load_serialized_classifier(classifier)

        self.classifier_id = classifier_id


    def predict(self, X, format_data=False, unwrap_prediction=False):
        if format_data is True:
            X = self.prepare_prediction_data(X)

        prediction = self.classifier.predict(X)

        if unwrap_prediction is True:
            prediction = prediction[0]

        return MarketPrediction(predictions_map[prediction])

    def train(self, X, y):
        self.classifier.fit(X,y)

    def prepare_training_data(self, strategy_data):
        X = []
        y = []

        features = strategy_data[0].keys()

        self.logger.info('Training Features', data=features)

        for tick in strategy_data:
            tick_data = strategy_data[tick]
            data = []
            for feature in features:
                if feature == STRATEGY_DECISION:
                    y.append(tick_data[feature])
                else:
                    data.append(tick_data[feature])
            X.append(data)

        return X, y

    def prepare_prediction_data(self, strategy_data):
        X = []

        features = strategy_data[0].keys()
        for tick in strategy_data:
            tick_data = strategy_data[tick]
            data = []
            for feature in features:
                if feature == STRATEGY_DECISION:
                    continue
                else:
                    data.append(tick_data[feature])
            X.append(data)

        return X

    def load(self, serialized_classifier):
        self._classifier = pkl.loads(serialized_classifier)

    def serialize(self):
        return pkl.dumps(self.classifier)
