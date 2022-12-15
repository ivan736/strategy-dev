import datetime
from collections import defaultdict

from indicators.base_indicators import *
from indicators.bar_size_indicators import *
from strategies.base_strategy import BaseStrategy
from utils.create_cerebro import create_cerebro
from data_loader import *
from loguru import logger

logger.add('steps.log')

OPEN_TIME = datetime.datetime.strptime('09:00', '%H:%M').time()
CLOSE_TIME = datetime.datetime.strptime('13:45', '%H:%M').time()
CLOSE_POISTION_TIME = datetime.datetime.strptime('13:40', '%H:%M').time()
TRADES = defaultdict(int)


class TeamLongStrategy(BaseStrategy):

    def __init__(self):
        self.valid_kbar = ValidLongKbarIndicator(self.datas[0])
        self.arrange = LongArrange(self.datas[0])

        self.sd_movav20 = btind.SimpleMovingAverage(self.datas[0], period=20)
        self.sd_movav60 = btind.SimpleMovingAverage(self.datas[0], period=60)
        self.ld_movav5 = btind.SimpleMovingAverage(self.datas[1], period=5)

        self.sd_slope_20 = self.sd_movav20(0) - self.sd_movav20(-1)
        self.sd_slope_60 = self.sd_movav60(0) - self.sd_movav60(-1)
        self.ld_slope_5 = self.ld_movav5(0) - self.ld_movav5(-1)

        self.stop_lost_price = None

    def _filter_time(self):
        if self.datas[0].datetime.time(0) < OPEN_TIME or self.datas[0].datetime.time(0) > CLOSE_POISTION_TIME:
            return True
        else:
            return False

    def _filter_trade_times(self):
        if TRADES[self.datas[0].datetime.date(0)] == 1 and self.datas[0].datetime.date(0).weekday() in (0, 1, 3, 4):
            return False
        elif TRADES[self.datas[0].datetime.date(0)] <= 3 and self.datas[0].datetime.date(0).weekday() == 2:
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

        c1 = self.data0.lines.close[0] > self.sd_movav20[0]
        c2 = self.data0.lines.close[0] > self.sd_movav60[0]
        c3 = self.data0.lines.close[0] > self.ld_movav5[0]
        c4 = self.sd_slope_20 > 0 and self.sd_slope_60 > 0 and self.ld_slope_5 > 0

        if self.valid_kbar[0] and c1 and c2 and c3 and c4 and self.arrange[0]:
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
    print(f'Final Portfolio Value: {c.broker.getvalue():.2f} with slope, filter trade times, allow Wed to 3 times, dont skip Monday, dayonly')
    print(f'Spent: {datetime.datetime.now() - start}')

# Final Portfolio Value: 100763.00 without slope
# Spent: 0:09:03.179574

# Final Portfolio Value: 101454.00 with slope
# Spent: 0:09:13.513725

# Final Portfolio Value: 101126.00 with slope, filter trade times, with arrange
#  Spent: 0:09:40.632068