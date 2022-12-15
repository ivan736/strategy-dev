import datetime
from collections import defaultdict

from indicators.base_indicators import *
from indicators.bar_size_indicators import *
from strategies.base_strategy import BaseStrategy
from utils.create_cerebro import create_cerebro
from data_loader import *

OPEN_TIME = datetime.datetime.strptime('09:00', '%H:%M').time()
CLOSE_TIME = datetime.datetime.strptime('13:45', '%H:%M').time()
CLOSE_POISTION_TIME = datetime.datetime.strptime('13:40', '%H:%M').time()
TRADES = defaultdict(int)


class TeamLongStrategy(BaseStrategy):

    def __init__(self):
        self.signal = ShortCrossLong2()
        self.stop_lost_price = None

    def _filter_time(self):
        if self.datas[0].datetime.time(0) < OPEN_TIME or self.datas[0].datetime.time(0) > CLOSE_POISTION_TIME:
            return True
        else:
            return False

    def _filter_trade_times(self):
        if not TRADES[self.datas[0].datetime.date(0)]:
            TRADES[self.datas[0].datetime.date(0)] += 1
            return False
        else:
            return True

    def next(self):
        if self._filter_time():
            return

        if self._filter_trade_times():
            return

        # close position before close market
        if self.datas[0].datetime.time(0) == CLOSE_POISTION_TIME:
            if self.position:
                self.close()
            return

        if self.signal[0]:
            if not self.position:
                self.buy(size=self.p.stake)
                self.stop_lost_price = self.datas[0].open[0]

        if self.stop_lost_price and self.datas[0].close[0] < self.stop_lost_price:
            if self.position:
                self.log(f'stop lost:{self.stop_lost_price}')
                self.close()


if __name__ == '__main__':
    start = datetime.datetime.now()

    c = create_cerebro(TeamLongStrategy)

    c.resampledata(data, name='five_min', timeframe=bt.dataseries.TimeFrame.Minutes, compression=5)
    c.replaydata(data, name='one_day', timeframe=bt.dataseries.TimeFrame.Days, compression=1)

    r = c.run()

    # Print out the final result
    print(f'Final Portfolio Value: {c.broker.getvalue():.2f} with base_indicators: ShortCrossLong2')
    print(f'Spent: {datetime.datetime.now() - start}')