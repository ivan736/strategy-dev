from datetime import date, datetime, time, timedelta
from time import sleep

import pandas as pd
from loguru import logger

from src.broker.kbar_fetcher import KbarFetcher
from src.src_trade.sql_operator import get_db_and_tb_operator

TRADE_TIME_PERIOD_1_START = time(8, 45, 0)
TRADE_TIME_PERIOD_1_STOP = time(13, 45, 0)
TRADE_TIME_PERIOD_2_START = time(3, 0, 0)
TRADE_TIME_PERIOD_2_SOP = time(5, 0, 0)


class DatabasePatcher:
    def __init__(self) -> None:
        self.db, self.tb = get_db_and_tb_operator()
        self._init_db()
        self.kf = KbarFetcher()

    def __del__(self) -> None:
        self.kf.logout()

    def _init_db(self):
        self.db.create_db_if_not_exists()
        self.tb.create_tables_if_not_exists()

    def wait_to_valid_time(self):
        now: datetime = datetime.now()

        if now.time() <= TRADE_TIME_PERIOD_1_START:
            start_time: datetime = datetime.combine(
                now.date(), TRADE_TIME_PERIOD_1_START
            )
            time_to_sleep: int = (start_time - now).seconds
            logger.info(f"Wait to {start_time}, sleep {time_to_sleep} seconds")
            sleep(time_to_sleep + 1)

        elif now.time() >= TRADE_TIME_PERIOD_1_STOP:
            tomorrow: date = now.date() + timedelta(days=1)
            start_time: datetime = datetime.combine(tomorrow, TRADE_TIME_PERIOD_1_START)
            time_to_sleep: int = (start_time - now).seconds
            logger.info(f"Wait to {start_time}, sleep {time_to_sleep} seconds")
            sleep(time_to_sleep + 1)

    def _stand_by(self):
        now = datetime.now().time()
        minutes_to_go = 5 - now.minute % 5
        seconds_to_go = 60 - now.second
        time_to_sleep = (minutes_to_go - 1) * 60 + seconds_to_go + 1
        logger.info(f"Wait to next 5 minutes, {time_to_sleep} seconds")
        sleep(time_to_sleep)

    def run(self):
        while True:
            df: pd.DataFrame = self.download_data()
            self.save_to_db(df)
            self._stand_by()

    def download_data(self) -> pd.DataFrame:
        def _is_valid_data():
            if df.empty:
                return False

            delta: pd.Timedelta = datetime.now() - df.index[-1]
            if delta.total_seconds() > 300:
                sleep(1)
                logger.error(f"last k-bar is: {df.index[-1]}, re-download")
                return False
            return True

        while True:
            self.wait_to_valid_time()
            today = str(datetime.now().date())
            kbars = self.kf.fetch_kbar(start=today, end=today)
            df: pd.DataFrame = self.kf.format_day(kbars)

            if _is_valid_data():
                logger.info("download data")
                return df

    def save_to_db(self, df: pd.DataFrame):
        df = df[["date", "time", "open", "high", "low", "close", "volume"]]
        df["date"] = df["date"].astype(str)
        df["time"] = df["time"].astype(str)
        record_list = df.to_records(index=False).tolist()

        # skip current (last) running k-bar
        self.tb.insert_many_data("price_table", record_list[:-1])
        logger.info(f"save to db, last one is :{record_list[-1]}")


if __name__ == "__main__":
    dp = DatabasePatcher()
    dp.run()
