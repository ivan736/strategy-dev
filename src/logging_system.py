import uuid
from datetime import datetime
from sys import stdout

from loguru import logger

from src.config import ONLINE_LOG_DIR

FORMAT_TIME_MESSAGE = "{time:YYYY-MM-DD at HH:mm:ss} | {message}"
FORMAT_MESSAGE = "{message}"


def setup_logger(gridsearch=False):
    log_dir = (
        f"{ONLINE_LOG_DIR}/gridsearch/{uuid.uuid1()}"
        if gridsearch
        else f"{ONLINE_LOG_DIR}/{datetime.now().strftime('%Y-%m-%d-%H:%M')}"
    )
    logger.remove()
    # level
    logger.add(
        f"{log_dir}/info.log",
        format=FORMAT_TIME_MESSAGE,
        filter=lambda record: record["level"].name == "INFO",
    )
    logger.add(
        f"{log_dir}/debug.log",
        format=FORMAT_TIME_MESSAGE,
        filter=lambda record: record["level"].name == "DEBUG",
    )
    logger.add(
        f"{log_dir}/warning.log",
        format=FORMAT_TIME_MESSAGE,
        filter=lambda record: record["level"].name == "WARNING",
    )

    # extra
    logger.add(
        stdout,
        format=FORMAT_TIME_MESSAGE,
        filter=lambda record: "console" in record["extra"],
    )
    logger.add(
        f"{log_dir}/indicators.log",
        format=FORMAT_MESSAGE,
        level="TRACE",
        filter=lambda record: "indicators" in record["extra"],
    )
    logger.add(
        f"{log_dir}/trade.log",
        format=FORMAT_TIME_MESSAGE,
        filter=lambda record: "trade" in record["extra"],
    )
    logger.add(
        f"{log_dir}/telegram.log",
        format=FORMAT_TIME_MESSAGE,
        filter=lambda record: "telegram" in record["extra"],
    )
    # trace time spent in db in trade.py
    logger.add(
        f"{log_dir}/db.log",
        format=FORMAT_TIME_MESSAGE,
        level="TRACE",
        filter=lambda record: "db" in record["extra"],
    )
    logger.add(
        f"{log_dir}/bot.log",
        format=FORMAT_TIME_MESSAGE,
        filter=lambda record: "bot" in record["extra"],
    )


class TradeBotLogger:
    @staticmethod
    def indicators(msg: str):
        logger.bind(indicators=True).trace(msg)

    @staticmethod
    def trade(msg: str):
        logger.bind(trade=True).info(msg)

    @staticmethod
    def telegram(msg: str):
        logger.bind(telegram=True).info(msg)

    @staticmethod
    def db(msg: str):
        logger.bind(db=True).trace(msg)

    @staticmethod
    def bot(msg: str):
        logger.bind(bot=True).info(msg)

    @staticmethod
    def console(msg: str):
        logger.bind(console=True).info(msg)
