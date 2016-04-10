from argparse import ArgumentParser

from trading.data.load_local_data import load_json


def main(data_file, classifier_id=None, strategy=None):
    data = load_json(data_file)


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('data_file', help='name of data file')
    parser.add_argument('--classifier_id', help='id of classifier')
    parser.add_argument('--strategy', help='id of trading strategies')

    args = parser.parse_args()

    main(args.data_file, args.classifier_id, args.strategy)