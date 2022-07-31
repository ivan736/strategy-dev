from time import sleep
from pathlib import Path

from requests.exceptions import JSONDecodeError
import pandas as pd
from pandas import DataFrame
from pandas.core.indexes.datetimes import DatetimeIndex
from tqdm import tqdm
from FinMind.data import DataLoader
from loguru import logger

# get this token from findmind website
API_TOKEN = ''
START_DATE = '1/1/2018'
END_DATE = '2/1/2018'
CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR / 'finmind'

api: DataLoader = DataLoader()
api.login_by_token(api_token=API_TOKEN)


def download_mtx(date: str) -> DataFrame:
    try:
        return api.taiwan_futures_tick(futures_id='MTX', date=date)
    except JSONDecodeError:
        logger.info(f'requests fail on {date}')
        return DataFrame()


if __name__ == '__main__':
    # remove stdout to avoid messing up console
    logger.remove()
    logger.add(f'finmind-requests.log', level='DEBUG')
    logger.add(f'findmind-fails.log', level='INFO')

    dates: DatetimeIndex = pd.date_range(start=START_DATE, end=END_DATE)

    for d in tqdm(dates):
        download_date: str = str(d.date())
        df: DataFrame = download_mtx(download_date)

        if df.size:
            df.to_csv(f'{DATA_DIR}/{download_date}')

        # there is a requests limit per hour
        sleep(20)
