from trading.live.exceptions import LiveTradingException, KeyboardInterruptMessage
from trading.strategy_runner.base import TradingStrategyRunner


class BacktestTradingStrategyRunner(TradingStrategyRunner):

    def __init__(self, strategy_config, broker, backtest_count):
        self.backtest_count = backtest_count
        super(BacktestTradingStrategyRunner).__init__(strategy_config, broker)

        broker.get_backtest_price_data(self.instrument, backtest_count, self.strategy.granularity)

    def tick(self):
        while self.tick_num < self.backtest_count:
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

        self.shutdown('End Backtest')
        self.analyze_backtest()

    def analyze_backtest(self):
        self.logger.info('Trading Results: Account {account}'.format(account=self.broker.account))
        self.logger.info('Trading Results: Portfolio {portfolio}'.format(portfolio=self.strategy.portfolio))
        self.logger.info('Trading Results: Num Orders {num_orders}'.format(num_orders=self.num_orders))




