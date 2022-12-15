import backtrader as bt


class ValidLongKbarIndicator(bt.Indicator):
    lines = ('long_k', )
    params = (('value', 5), )

    def __init__(self) -> None:
        self.c1 = self.data0.close > self.data0.open
        self.c2 = self.data0.close - self.data0.open > (self.data0.high -
                                                        self.data0.close) + (self.data0.open - self.data0.low)
        self.lines.long_k = bt.And(self.c1, self.c2)

    # # equals to
    # def next(self):
    #     c1 = self.data0.close[0] > self.data0.open[0]
    #     c2 = self.data0.close[0] - self.data0.open[0] > (self.data0.high[0] - self.data0.close[0]) + (self.data0.open[0] - self.data0.low[0])
    #     self.lines.long_k[0] = c1 and c2


class ValidShortKbarIndicator(bt.Indicator):
    lines = ('short_k', )
    params = (('value', 5), )

    def __init__(self) -> None:
        self.c1 = self.data.open > self.data.close
        self.c2 = self.data.open - self.data.close > (self.data.high -
                                                      self.data.open) + (self.data.close - self.data.low)
        self.lines.short_k = bt.And(self.c1, self.c2)
