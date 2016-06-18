from bson import ObjectId

from trading.live.exceptions import LiveTradingException, KeyboardInterruptMessage

from trading.classifier import CLASSIFIERS
from trading.strategy_runner.base import TradingStrategyRunner

class TrainingStrategyRunner(TradingStrategyRunner):
    _logger = None
    training_data = {}

    def __init__(self, strategy_config, broker, num_training_points):
        self.num_training_points = num_training_points
        super(TrainingStrategyRunner).__init__(strategy_config, broker)

        classifier_config = strategy_config['classifier_config']

        classifier_name = classifier_config.get('classifier_name')
        self.classifier_name = classifier_name
        self.classifier = CLASSIFIERS[classifier_name](classifier_config)

    def tick(self):
        while self.tick_num < self.num_training_points:
            try:
                account_information = self.broker.get_account_information()
                self.strategy.portfolio.update_account_portfolio_data(account_information)

                order_responses = self.get_order_updates()

                self.strategy.update_portfolio(order_responses)
                order_ids = order_responses.keys()
                self.remove_recorded_orders(order_ids)

                historical_market_data = self.broker.get_historical_price_data(self.instrument,
                                                                               count=self.strategy.data_window,
                                                                               granularity=self.strategy.granularity,
                                                                               tick=self.tick_num)

                current_market_data = self.broker.get_current_price_data(instrument=self.instrument, tick=self.tick_num)

                self.strategy.analyze_data({
                    'historical': historical_market_data,
                    'current': current_market_data
                })

                order_decision, market_order = self.strategy.make_decision()
                order_response = self.make_market_order(order_decision, market_order)

                self.update_orders(order_response)

                self.training_data[self.tick_num] = self.strategy.strategy_data

                self.tick_num += 1

            except (KeyboardInterrupt, SystemExit) as e:
                self.logger.error('Manually Stopped Live Trading', data=e)
                self.shutdown(KeyboardInterruptMessage)
                break
            except LiveTradingException as e:
                self.logger.error('Live Trading Error', data=e)
                self.shutdown(e)
                break
            except Exception as e:
                self.logger.error('Uncaught Error', data=e)
                self.shutdown(e)
                break

        self.train_classifier()
        self.shutdown('Successful Training')

    def train_classifier(self):
        X, y = self.classifier.prepare_training_data(self.training_data)
        self.classifier.train(X, y)

    def shutdown(self, shutdown_cause):
        serialized_classifier = self.classifier.serialize()
        self.db.insert_one({'_id': ObjectId(self.classifier.classifier_id), 'strategy': self.strategy.name,
                            'classifier': serialized_classifier, 'name': serialized_classifier})




