import backtrader.analyzers as btanalyzers
import backtrader as bt
from loguru import logger

def create_cerebro(strategy):
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # cerebro.addstrategy(MyStrategy, period=90)
    cerebro.addstrategy(strategy)

    # Add the Data Feed to Cerebro
    # cerebro.adddata(data)
    # cerebro.resampledata(data, timeframe=bt.dataseries.TimeFrame.Minutes, compression=5)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # set sizer
    cerebro.addsizer(bt.sizers.SizerFix, stake=1)

    # Print out the starting conditions
    logger.info(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')

    cerebro.addanalyzer(btanalyzers.DrawDown, _name="DrawDown")
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name="TradeAnalyzer")
    cerebro.addanalyzer(btanalyzers.Transactions, _name="Transactions")

    cerebro.broker.setcommission(commission=1.0, margin=800)

    return cerebro