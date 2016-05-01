import datetime
from collections import OrderedDict

from trading.classifier import RFClassifier
from trading.db import get_database


PATTERNS = ('buy', 'sell')


def prepare_training_data(candles):
    X = []
    y = []

    formatted_candle_data = {}

    for candlestick in candles:
        features = candlestick['candle']
        date = candlestick['date']
        pattern = candlestick.get('pattern', 'stay')
        id = candlestick.get('id')
        formatted_candle_data[id] = {'features': features, 'date': date, 'pattern': pattern}

    features = candles[0]['candle'].keys()

    sorted_candle_data = OrderedDict(sorted(formatted_candle_data.items(), key = lambda t: t[0]))

    for dt in sorted_candle_data:
        candle_data = sorted_candle_data[dt]
        candle_features = candle_data['features']
        data = []
        for feature in features:
            data.append(candle_features[feature])
        y.append(candle_data['pattern'])
        X.append(data)

    return X, y


def main():
    db = get_database()
    chart_data = db.candle_data.find_one({})
    candles = chart_data['candles']
    config = {'classifier_id': None}

    classifier = RFClassifier(config)
    X, y = prepare_training_data(candles)
    print('Initiating Training for chart {chart} at time {dt}'.format(chart=chart_data['_id'], dt=datetime.datetime.now()))
    print('Num Candles: ' +  str(len(X)))
    classifier.train(X, y)
    print('Training Complete at {dt}'.format(dt=datetime.datetime.now()))


if __name__ == '__main__':
    main()