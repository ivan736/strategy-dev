from pathlib import Path

import shioaji as sj
import pandas as pd

USER = ''
PASSWORD = ''
CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR / 'shioaji'

api = sj.Shioaji()
accounts = api.login(USER, PASSWORD)


def download_kbars(contract=api.Contracts.Futures.TXF.TXFR1, start='2021-01-01', end='2021-12-31'):
    kbars = api.kbars(contract, start=start, end=end)
    df = pd.DataFrame({**kbars})
    df.ts = pd.to_datetime(df.ts)
    df.to_csv(f'{DATA_DIR}/{start}-to-{end}.csv')


if __name__ == '__main__':
    download_kbars(api.Contracts.Futures.TXF.TXFR1, '2020-01-01', '2020-12-31')