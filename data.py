import pdb
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import FinanceDataReader as fdr
from tqdm import tqdm

def fetch_k200_list() :

    print('KOSPI200 종목 리스팅...')
    stock_list = []
    for page in tqdm(range(20)) : 
        url = f'https://finance.naver.com/sise/entryJongmok.naver?type=KPI200&page={page+1}'
        response = requests.get(url)
        response.encoding = 'euc-kr'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.find_all('td', {'class' : 'ctg'})
        for row in rows : 
            code = row.find('a')['href'].split("=")[-1]
            name = row.text
            stock_list.append([code, name])
        
        time.sleep(0.2)

    stock_list = pd.DataFrame(stock_list, columns = ['종목코드', '종목명'])
    stock_list.to_json('k200_list.json', orient='records')
    
    return stock_list

def fetch_k200_price(stock_list) : 
    
    print('KOSPI200 종목 가격 크롤링...')
    data = pd.DataFrame()
    for code in tqdm(stock_list['종목코드']) :
        try : 
            buffer = fdr.DataReader(code, start='2024-01-01', end = '2024-12-31')
            buffer['Code'] = code
            
            data = pd.concat([data, buffer])
        except :
            print(f"오류 : {code}")
    
    data = data.reset_index()
    data.to_json('k200_price.json', orient='records')

    return data

if __name__ == '__main__' : 

    stock_list = fetch_k200_list()
    price = fetch_k200_price(stock_list)
