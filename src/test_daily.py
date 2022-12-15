import datetime

import backtrader as bt
import backtrader.indicators as btind

from indicators.base_indicators import TeamLong
from strategies.base_strategy import BaseStrategy
from utils.create_cerebro import create_cerebro
from utils.init_logger import setup_logger
from data_loader import data


class TeamLongStrategy(BaseStrategy):

    def __init__(self):
        day_movav5 = btind.SimpleMovingAverage(self.datas[1], period=5)
        c1 = self.data0.lines.close > day_movav5

        c2 = TeamLong()
        
        self.signal = bt.And(c1, c2)

        self.stop_lost_price = None

    def next(self):
        self._debug(self.datas[0])

        if self._filter_time():
            return

        # close position before close market
        if self.datas[0].datetime.time(0) == self.p.close_position_time:
            if self.position:
                self.close()
            return

        if self.signal:
            if self._filter_trade_times():
                return

            if not self.position:
                self.buy(size=self.p.stake)
                self.stop_lost_price = self.datas[0].open[0]

        if self.stop_lost_price and self.datas[0].close[0] < self.stop_lost_price:
            if self.position:
                self.close()


if __name__ == '__main__':
    setup_logger()

    start = datetime.datetime.now()

    c = create_cerebro(TeamLongStrategy)

    c.resampledata(data, name='five_min', timeframe=bt.dataseries.TimeFrame.Minutes, compression=5)
    c.replaydata(data, name='one_day', timeframe=bt.dataseries.TimeFrame.Days, compression=1)

    r = c.run()

    # Print out the final result
    print(f'Final Portfolio Value: {c.broker.getvalue():.2f}')
    print(f'Spent: {datetime.datetime.now() - start}')