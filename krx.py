import numpy as np
import pandas as pd
import requests
import io
from tqdm import tqdm
import time
import logging
import pdb
import holidays

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("krx.log", encoding="utf-8"),  # 파일 저장
        logging.StreamHandler()  # 콘솔 출력
    ]
)






def get_trading_amount_by_date(isuCd, stock_code, stock_name, date):

    url = 'https://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'

    otp_params = {
        'locale': 'ko_KR',
        'inqTpCd': 1,
        'trdVolVal': 2,
        'askBid': 3,
        'tboxisuCd_finder_stkisu0_2': f'{stock_code}/{stock_name}',
        'isuCd': isuCd,
        'isuCd2': isuCd,
        'codeNmisuCd_finder_stkisu0_2': stock_name,
        'param1isuCd_finder_stkisu0_2': 'ALL',
        'strtDd': date,
        'endDd': date,
        'share': 1,
        'money': 1,
        'csvxls_isNo': False,
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT02301'
    }
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}
    
    
    otp = requests.post(url, params=otp_params, headers=headers).text
    download_params = {
        'code': otp,
    }
    download_url = "https://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
    response = requests.post(download_url, params=download_params, headers=headers)
    
    if response.status_code == 200:
    
        data = pd.read_csv(io.BytesIO(response.content), encoding='euc-kr', dtype={'단축코드': 'string'})
        data['date'] = date
        data['stock_code'] = stock_code
        data['stock_name'] = stock_name

    else:
        data = pd.DataFrame()
        logging.warning(f"Failed to download data for {stock_code} on {date}")
        
    
    wait = np.random.uniform(0, 0.5)  # 0~0.3초 사이의 랜덤한 대기 시간
    time.sleep(wait)  # 너무 빠르게 요청하면 차단될 수 있으므로 잠시 대기

    return data


if __name__ == "__main__":

    krx_code = pd.read_csv('krx_code.csv', dtype={'단축코드': 'string'}, encoding='euc-kr')
    krx_code = krx_code[['표준코드', '단축코드', '한글 종목약명']]
    
    
    date_list = pd.date_range(start='20240222', end='20241231')
    kr_holidays = holidays.KR(years=2024)
    date_list = [date for date in date_list if date.weekday() < 5 and date not in kr_holidays]  # 주말 및 공휴일 제외
    
    for date in date_list:
        
        date = date.strftime('%Y%m%d')
        print(date)

        data = pd.DataFrame()
        a = time.time()

        for i, row in krx_code.iterrows():

            isuCd = row['표준코드']
            stock_code = row['단축코드']
            stock_name = row['한글 종목약명']
            
            b = time.time()
            c = int(b - a)
            h, m, s = c // 3600, (c % 3600) // 60, c % 60
            progress = (i + 1) / len(krx_code) * 100

            print(f"{stock_code} | Processing {i + 1}/{len(krx_code)} ({progress:.2f}%) | {h}h {m}m {s}s | Size : {len(data)} ", end="\r")

            buffer = get_trading_amount_by_date(isuCd, stock_code, stock_name, date)
            data = pd.concat([data, buffer], axis=0)
            

        data.reset_index(drop=True, inplace=True)
        data.to_csv(f'data/{date}_trading_data.csv', index=False, encoding='euc-kr')
