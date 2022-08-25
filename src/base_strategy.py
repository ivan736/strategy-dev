from abc import abstractmethod

import backtrader as bt
from indicators.base_indicators import *
from loguru import logger


class BaseStrategy(bt.Strategy):
    # only ma across
    params = dict(period=20, stake=1, only_long=True)

    @abstractmethod
    def __init__(self):
        pass

    def log(self, txt, dt=None):
        """Logging function for this strategy"""
        dt = dt or f'{self.datas[0].datetime.date(0)} {self.datas[0].datetime.time(0)}'
        logger.info(f'{dt}\t{txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}'
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            else:  # Sell
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}'
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # self.order = None

    def next(self):
        if self.buy_signal:
            if not self.position:
                self.buy(size=self.p.stake)

        if self.sell_signal:
            if self.position:
                self.close()

    def _debug(self, data):
        logger.debug(
            f'Open: {data.open[0]:8.1f}\tClose: {data.close[0]:8.1f}\tHigh: {data.high[0]:8.1f}\tLow: {data.low[0]:8.1f}'
        )
