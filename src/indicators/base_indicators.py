import backtrader as bt
import backtrader.indicators as btind

from .bar_size_indicators import ValidLongKbarIndicator


class MeanAverageBaseIndicator(bt.Indicator):
    params = (('value', 5), )

    def __init__(self) -> None:
        self.movav5 = btind.SimpleMovingAverage(self.datas[0], period=5)
        self.movav10 = btind.SimpleMovingAverage(self.datas[0], period=10)
        self.movav20 = btind.SimpleMovingAverage(self.datas[0], period=20)
        self.movav60 = btind.SimpleMovingAverage(self.datas[0], period=60)


class LongArrange(MeanAverageBaseIndicator):
    # Final Portfolio Value: 105343.00 with base_indicators: LongArrange
    lines = ('arrange', )

    def __init__(self) -> None:
        super().__init__()
        self.c1 = self.movav5 > self.movav20
        self.c2 = self.movav20 > self.movav60

        self.lines.arrange = bt.And(self.c1, self.c2)


class ShortCrossLongAndLongArrange(MeanAverageBaseIndicator):
    # Final Portfolio Value: 105639.00 with base_indicators: ShortCrossLongAndLongArrange
    lines = ('cross', )

    def __init__(self) -> None:
        super().__init__()
        self.long_arrange = LongArrange()
        self.c = btind.CrossOver(self.movav20, self.movav60)
        self.lines.cross = bt.And(self.long_arrange, self.c)


class ShortCrossLong(MeanAverageBaseIndicator):
    # Final Portfolio Value: 107339.00 with base_indicators: ShortCrossLong
    lines = ('cross', )

    def __init__(self) -> None:
        super().__init__()
        self.lines.cross = btind.CrossOver(self.movav5, self.movav60)


class ShortCrossLong2(MeanAverageBaseIndicator):
    # Final Portfolio Value: 105518.00 with base_indicators: ShortCrossLong2
    lines = ('cross', )

    def __init__(self) -> None:
        super().__init__()
        self.lines.cross = btind.CrossOver(self.movav20, self.movav60)


class TeamLong(MeanAverageBaseIndicator):
    lines = ('signal', )

    def __init__(self) -> None:
        super().__init__()
        valid_k_bar = ValidLongKbarIndicator()
        slope_ma5 = self.movav5(0) - self.movav5(-1)

        c1 = self.datas[0].lines.close > self.movav20
        c2 = self.datas[0].lines.close > self.movav60
        c3 = slope_ma5 > 0

        j1 = bt.And(c1, c2)
        j2 = bt.And(c3, valid_k_bar)

        self.lines.signal = bt.And(j1, j2)