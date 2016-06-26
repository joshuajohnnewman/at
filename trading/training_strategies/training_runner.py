import copy

from bson import ObjectId

from trading.live.exceptions import LiveTradingException, KeyboardInterruptMessage

from trading.classifier import CLASSIFIERS
from trading.strategy_runner.base import TradingStrategyRunner


class TrainingStrategyRunner(TradingStrategyRunner):
    _logger = None
    training_data = {}

    def __init__(self, strategy_config, broker, num_training_points):
        self.num_training_points = num_training_points
        super(TrainingStrategyRunner, self).__init__(strategy_config, broker)

        classifier_config = strategy_config['classifier_config']

        classifier_name = classifier_config.get('classifier_name')
        self.classifier_name = classifier_name
        self.classifier = CLASSIFIERS[classifier_name](classifier_config)

        broker.get_backtest_price_data(self.instrument, num_training_points + 1000, self.strategy.granularity)

    def tick(self):
        while self.tick_num < self.num_training_points:
            try:
                account_information = self.broker.get_account_information()
                self.strategy.portfolio.update_account_portfolio_data(account_information)

                order_responses = self.get_order_updates()

                self.update_strategy_portfolio(order_responses)

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

                strategy_data = self.strategy.strategy_data
                strategy_data['decision'] = order_decision
                self.logger.info('Strat Data', data=strategy_data)
                self.logger.info('Strat Data Tick', data=self.tick_num)
                self.training_data[self.tick_num] = copy.copy(strategy_data)

                order_response = self.make_market_order(order_decision, market_order)

                self.update_orders(order_response)

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

    def train_classifier(self):
        self.logger.info('Training')
        X, y = self.classifier.prepare_training_data(self.training_data)
        self.classifier.train(X, y)

    def shutdown(self, shutdown_cause):
        self.train_classifier()
        serialized_classifier = self.classifier.serialize()
        self.db.classifiers.insert_one({'_id': ObjectId(self.classifier.classifier_id), 'strategy': self.strategy.name,
                                        'classifier': serialized_classifier, 'name': serialized_classifier})
        self.logger.info('Trained Classifier', data=self.classifier.classifier_id)




