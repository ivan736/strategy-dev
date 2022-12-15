import datetime

import backtrader as bt
import backtrader.feeds as btfeeds


class MyWebData(btfeeds.GenericCSVData):
    params = (
        ('fromdate', datetime.datetime(2022, 1, 1)),
        ('todate', datetime.datetime(2022, 12, 31)),
        ('timeframe', bt.dataseries.TimeFrame.Minutes),
        ('nullvalue', 0.0),
        ('dtformat', ('%Y/%m/%d')),
        ('tmformat', ('%H:%M:%S')),
        ('datetime', 0),
        ('time', 1),
        ('high', 3),
        ('low', 4),
        ('open', 2),
        ('close', 5),
        ('volume', 6),
        ('openinterest', -1),
    )

data = MyWebData(dataname='../data/jason/dayonly-20010101-20220817.csv')