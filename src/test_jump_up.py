import datetime

from loguru import logger
import backtrader as bt
import backtrader.indicators as btind

from indicators.base_indicators import ShortCrossLong, LongArrange
from strategies.base_strategy import BaseStrategy
from utils.create_cerebro import create_cerebro
from data_loader import data


class ArrangeStrategy(BaseStrategy):
    params = dict(period=20, stake=1, only_long=True)

    def __init__(self):
        s1 = ShortCrossLong()
        s2 = LongArrange()
        self.buy_signal = bt.And(s1 > 0, s2)
        self.sell_signal = s2 < 1


class JumpUp(BaseStrategy):
    params = dict(period=20, stake=1, only_long=True)

    def __init__(self):
        self.long_arrange = LongArrange()
        self.movav5 = btind.SimpleMovingAverage(self.data, period=5)

    def next(self):
        if self.datas[0].open - self.datas[-1].close > 20 and self.long_arrange:
            if not self.position:
                logger.info(f'buy {self.datas[0].datetime.date(0)}')
                self.buy(size=self.p.stake)
        elif self.data.close < self.movav5:
            if self.position:
                self.close()
                logger.info(f'sell {self.datas[0].datetime.date(0)}')


if __name__ == '__main__':
    start = datetime.datetime.now()

    c = create_cerebro(JumpUp)
    c.resampledata(data, name='five_min', timeframe=bt.dataseries.TimeFrame.Minutes, compression=5)
    
    r = c.run()

    # Print out the final result
    logger.info(f'Final Portfolio Value: {c.broker.getvalue():.2f}')
    logger.info(f'Spent: {datetime.datetime.now() - start}')