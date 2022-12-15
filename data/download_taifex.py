import re
from pathlib import Path
from typing import List
from zipfile import ZipFile

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

TAIFEX_DOWNLOAD_PAGE = 'https://www.taifex.com.tw/cht/3/dlFutPrevious30DaysSalesData'
CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR / 'taifex'


def get_csv_links() -> List[str]:
    response = requests.get(TAIFEX_DOWNLOAD_PAGE)
    soup = BeautifulSoup(response.text, 'html.parser')
    url_pattern = re.compile('(https.*zip)')

    # <input name="button7" type="button" class="btn_orange" id="button7"
    # onclick="javascript:window.open('https://www.taifex.com.tw/file/taifex/Dailydownload/Dailydownload/Daily_2022_08_01.zip')"
    # value="下載" title="前30個交易日期貨每筆成交資料rpt格式(zip檔)">
    links: List[str] = [
        _['onclick'] for _ in soup.find_all('input', id='button7') if _['value'] == '下載' and 'csv' in _['title']
    ]
    links: List[str] = [url_pattern.search(_).group() for _ in links]
    return links


def download_and_extract_file(url: str) -> str:
    file_name: str = url.split('/')[-1]
    file_path: Path = Path(f'{DATA_DIR}/{file_name}')

    if file_path.exists() and file_path.stat().st_size > 0:
        return ''

    with requests.get(url, stream=True) as r:
        with file_path.open('wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    unzip_file(file_path)
    file_path.unlink()
    return file_name


def unzip_file(file_path: str):
    ZipFile(file_path).extractall(DATA_DIR)


if __name__ == '__main__':
    csv_links: List[str] = get_csv_links()

    for link in tqdm(csv_links):
        download_and_extract_file(link)