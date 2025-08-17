import pdb
import numpy as np
import pandas as pd
from config import *
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

class Environment() :
    def __init__(self):
        self.interest_rate = 1.0
        self.news = ""
        self.today_price = pd.DataFrame()

    def update(self) :
        """
        매 기말에 실행하여 환경을 업데이트
        """
        self.interest_rate += np.random.random()

    def generate_news(self) :
        """
        OpenAI API를 이용해서 뉴스를 생성할 함수
        """
        
        keyword_list = ['탄핵', '상법개정', '관세', '트럼프', '연준', '주가조작', '민생소비']
        idx = np.random.choice(range(len(keyword_list)))
        keyword = keyword_list[idx]
        prompt = news_prompt + f"키워드는 {keyword}"
        news = self.openai(prompt)
        self.news = f"{np.random.random():.2f}:{news}"
        
    
        
    def openai(self, prompt) :
        return prompt

    def stock(self) :
        pass


class Agent() :
    _counter = 0
    style_list = [  # 은행에서 하는 투자성향 분류로 이후 변경
        '기관투자자/공격적투자',
        '기관투자자/보수적투자',
        '개인투자자/공격적투자',
        '개인투자자/보수적투자',
    ]
    

    def __init__(self, env:Environment):
        self.env = env
        self.consideration = {} # 투자 시 염두에 둘 사항들
        self.balance = 0
        self.decision = None
        self.portfolio = {}
        self.trading_book = []

        self.set_agent_profile()
    
    def set_agent_profile(self) :
        self.id = self.set_id()
        self.balance = np.random.randint(500, 1000, 1) # 예산

        self.consideration['style'] = self.style_list[self.id]
        self.consideration['risk_limit'] = np.random.randint(1, 100, 1) # 리스크 한도(Risk tolerance)
        # self.consideration['investment_propensity'] = np.random.choice(['공격', '안정', '중립']) # 투자 성향

    # 기본값 설정
    def set_id(self) :
        self.id = type(self)._counter
        type(self)._counter += 1
        return self.id

    # 투자자 행동
    def act(self) :
        print('투자자 행동')

        # 투자 고려사항 업데이트
        self.read_market_price()
        self.read_news()
                
        # 투자 집행
        self.do_investment()

    def read_market_price(self) :
        print(f'Agent {self.id} : 가격을 확인함')
        self.consideration['today_price'] = env.today_price.to_dict(orient='records')

    def read_news(self) :
        # 50% 확률로 생성된 뉴스를 읽음
        # 이후에 성향에 따라 모델링하는 방향 도입 (기관투자자가 더 잘 읽는다거나?)

        if np.random.random() > 0.5 :            
            print(f'Agent {self.id} : 뉴스를 읽음')
            self.news = env.news
            self.consideration['news'] = self.news
        
        else :
            self.consideration['news'] = None


    def do_investment(self) :
        
        print(f'Agent {self.id} : 주요사항 검토')
        decision = self.make_decision()
        
        if decision : 
            self.update() # 집행한 결과 반영

    def make_decision(self) :
        role = f"""
        {self.consideration["style"]}의 투자스타일을 갖는 투자자
        """
        
        prompt = f"""
        아래 사항을 고려해서 투자 결정을 내려줘
        투자를 할 경우 변경할 포트폴리오를 반환해주되 투자할 종목코드를 key로, 체결가격과 수량을 item으로 하는 딕셔너리로 응답해줘
        투자를 하지 않을 경우는 null값을 응답

        1. 현재 잔액 : {self.balance}
        2. 현재 포트폴리오 : {self.portfolio}
        3. 리스크 한도 : {self.consideration["risk_limit"]}
        4. 현재 주가 : {self.consideration["today_price"]}        
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 텍스트 응답용 최신 모델
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,   # 창의성 정도 (0 = 정확성, 1 = 창의성)
            )
        
        return response

    def update(self) :
        # 포트폴리오 변경 내용에 따라 잔액을 수정하고, 수익률을 계산
        trade_fee = 10
        self.balance -= trade_fee

        profit = 0.01
        self.trading_book.append([date, profit])


if __name__ == '__main__' :

    # 시뮬레이션 기본값 설정
    num_agent = 4

    # 환경 생성
    price = pd.read_json('k200_price.json', dtype = {'Code' : str})
    date_list = price['Date'].drop_duplicates()

    env = Environment()

    # 에이전트 생성
    agent = [Agent(env) for _ in range(num_agent)]

    # 시뮬레이션
    for idx, date in enumerate(date_list) :
        print(f"{idx+1: 3}일차|{date}|")
        
        # 환경 업데이트
        # 1. 오늘의 가격 입력
        # 데이터 스누핑 방지를 위해 종가는 미제공 / 이후에 과거 가격도 일부 제공하는 걸로 변경할 필요 있음
        env.today_price = price[price['Date'] == date][['Open', 'High', 'Low', 'Code']]
       
        # 뉴스 생성 / 외부 shock
        env.generate_news()

        for i in range(num_agent) :
            agent[i].act()
                        
        # 환경 업데이트
        env.update()