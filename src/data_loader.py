import datetime

import backtrader as bt
import backtrader.feeds as btfeeds


class MyWebData(btfeeds.GenericCSVData):
    params = (
        # ('fromdate', datetime.datetime(2022, 1, 1)),
        # ('todate', datetime.datetime(2022, 12, 31)),
        ('fromdate', datetime.datetime(2001, 1, 1)),
        ('todate', datetime.datetime(2001, 1, 31)),
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

# down
# data = MyWebData(dataname='../data/jason/allday-20170515-20220817.csv')
# 2017 101036.00
# 2018 98695.00
# 2019 102000.00


# up
data = MyWebData(dataname='../data/jason/dayonly-20010101-20220817.csv')
# 2017 100422.00
# 2018 98755.00
# 2019 102032.00


# data = MyWebData(dataname='../data/website/TXF20110101_20201231.csv')
# data = MyWebData(dataname='../data/website/TXF20210101_20211231.csv')
