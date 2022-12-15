import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import shioaji as sj
from dotenv import load_dotenv
from loguru import logger

from src.config import ONLINE_LOG_DIR

load_dotenv()


class KbarFetcher:
    def __init__(self) -> None:
        self.api = sj.Shioaji()
        USER = os.environ["SHIOAJI_USER"]
        PASSWORD = os.environ["SHIOAJI_PASSWORD"]
        self.accounts = self.api.login(USER, PASSWORD)

    def fetch_kbar(
        self, contract=None, start: str = "2022-09-02", end: str = "2022-09-02"
    ) -> pd.DataFrame:
        """
        return Dataframe: open, high, low, close, volume, date, time
        """
        start = start if start else self._today()
        end = end if end else self._today()
        # small -> MXF
        contract = contract if contract else self.api.Contracts.Futures.TXF.TXFR1

        kbars = self.api.kbars(contract, start=start, end=end)
        df = pd.DataFrame({**kbars})
        return df

    def logout(self) -> None:
        self.api.logout()

    def _today(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def format_day(self, df: pd.DataFrame, half_day=True) -> pd.DataFrame:
        df.columns = df.columns.str.lower()
        df["datetime"] = pd.to_datetime(df["ts"])
        df = df.set_index("datetime")

        if half_day:
            df = df.between_time("08:45:00", "13:45:00")
            self._debug_1k(df)

        df = df.groupby(pd.Grouper(freq="5min", closed="right")).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        df["date"] = df.index.date
        df["time"] = df.index.time
        df = df[df.open.notna()]
        return df

    def _debug_1k(self, df: pd.DataFrame):
        log_dir = Path(f"{ONLINE_LOG_DIR}/debug")
        if not log_dir.exists():
            log_dir.mkdir()

        log_file = f"{ONLINE_LOG_DIR}/debug/{datetime.now().strftime('%Y-%m-%d-%H:%M')}"
        df.to_csv(log_file)
