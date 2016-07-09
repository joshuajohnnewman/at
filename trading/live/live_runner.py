import time

from trading.live.exceptions import LiveTradingException, KeyboardInterruptMessage
from trading.strategy_runner.base import TradingStrategyRunner


class LiveTradingStrategyRunner(TradingStrategyRunner):
    def __init__(self, strategy_config, broker):
        super(LiveTradingStrategyRunner, self).__init__(strategy_config, broker)

    def tick(self):
        while True:
            try:
                account_information = self.broker.get_account_information()
                self.strategy.portfolio.update_account_portfolio_data(account_information)

                order_responses = self.get_order_updates()
                self.update_strategy_portfolio(order_responses)
                self.remove_recorded_orders(order_responses)

                historical_market_data = self.broker.get_historical_price_data(self.strategy.data_window,
                                                                               granularity=self.strategy.granularity)

                current_market_data = self.broker.get_current_price_data()

                self.strategy.analyze_data({
                    'historical': historical_market_data,
                    'current': current_market_data
                })

                self.strategy.log_strategy_data()

                order_decision, market_order = self.strategy.make_decision()

                order_response = self.make_market_order(order_decision, market_order)

                self.update_orders(order_response)

                time.sleep(self.interval)

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




