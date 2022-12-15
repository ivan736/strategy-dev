import datetime
from abc import abstractmethod
from collections import defaultdict

from loguru import logger
import backtrader as bt

OPEN_TIME = datetime.datetime.strptime('09:00', '%H:%M').time()
CLOSE_TIME = datetime.datetime.strptime('13:45', '%H:%M').time()
CLOSE_POISTION_TIME = datetime.datetime.strptime('13:40', '%H:%M').time()
TRADES = defaultdict(int)


class BaseStrategy(bt.Strategy):
    # only ma across
    params = dict(
        period=20,
        stake=1,
        only_long=True,
        open_time=OPEN_TIME,
        close_time=CLOSE_TIME,
        close_position_time=CLOSE_POISTION_TIME,
        trade_limit=TRADES
    )

    @abstractmethod
    def __init__(self):
        pass

    def log(self, txt, dt=None):
        """Logging function for this strategy"""
        dt = dt or f'{self.datas[0].datetime.date(0)} {self.datas[0].datetime.time(0)}'
        logger.info(f'{dt}\t{txt}')

    def _debug(self, data):
        dt =  f'{self.datas[0].datetime.date(0)} {self.datas[0].datetime.time(0)}'
        logger.debug(
            f'{dt}\tOpen: {data.open[0]:8.1f}\tClose: {data.close[0]:8.1f}\tHigh: {data.high[0]:8.1f}\tLow: {data.low[0]:8.1f}'
        )


    def _filter_time(self):
        if self.datas[0].datetime.time(0) < OPEN_TIME or self.datas[0].datetime.time(0) > CLOSE_POISTION_TIME:
            return True
        else:
            return False

    def _filter_trade_times(self):
        if not self.p.trade_limit[self.datas[0].datetime.date(0)]:
            self.p.trade_limit[self.datas[0].datetime.date(0)] += 1
            return False
        else:
            return True

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

    @abstractmethod
    def next(self):
        pass
