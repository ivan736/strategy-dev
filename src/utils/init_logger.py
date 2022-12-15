from sys import stdout

from loguru import logger


def setup_logger():
    logger.remove()
    logger.add(stdout, format='{message}')
    logger.add('info.log', format='{message}', filter=lambda record: record['level'].name == 'INFO')
    logger.add('debug.log', format='{message}', filter=lambda record: record['level'].name == 'DEBUG')
