import pickle as pkl

from bson import ObjectId
from sklearn import ensemble

from trading.classifier.base import Classifier, MarketPrediction
from trading.classifier.constants import STRATEGY_DECISION


class RFClassifier(Classifier):

    num_estimators = 10

    _training_data = None

    def __init__(self, config):
        classifier_id = config['classifier_id']
        self.features = config['features']

        if classifier_id is None:
            classifier_id = ObjectId()
            self.classifier = ensemble.RandomForestClassifier(n_estimators=self.num_estimators)
        else:
            self.classifier = self.load(classifier_id)

        super(RFClassifier, self).__init__(config)
        self.classifier_id = classifier_id

    def predict(self, X, format_data=False, unwrap_prediction=False):
        if format_data is True:
            X = self.prepare_prediction_data(X)

        prediction = self.classifier.predict(X)

        if unwrap_prediction is True:
            prediction = prediction[0]
            if prediction != 'buy':
                self.logger.info('JJPREDICTION', prediction)
            else:
                self.logger.info('KKPREDICTION', prediction)


        return MarketPrediction(prediction)

    def train(self, X, y):
        self.classifier.fit(X,y)

    def prepare_training_data(self, strategy_data):
        X = []
        y = []

        for tick in strategy_data:
            tick_data = strategy_data[tick]
            data = []
            for feature in self.features:
                if feature == STRATEGY_DECISION:
                    y.append(tick_data[feature])
                else:
                    data.append(tick_data[feature])
            X.append(data)

        return X, y

    def prepare_prediction_data(self, strategy_data):
        X = []

        data = []
        for feature in self.features:
            value = strategy_data[feature]
            if 'price' in feature:
                continue
            data.append(value)
        X.append(data)

        return X

    def load(self, classifier_id):
        classifier = self.db.classifiers.find_one({'_id': ObjectId(classifier_id)})
        return pkl.loads(classifier['classifier'])

    def serialize(self):
        return pkl.dumps(self.classifier)
