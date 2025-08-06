import pdb
import numpy as np
from config import *

class Environment() :
    def __init__(self):
        self.interest_rate = 1.0
        self.news = ""

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
    

    def __init__(self, env:Environment):
        self.env = env
        self.consideration = {} # 투자 시 염두에 둘 사항들
        self.decision = None

        self.set_agent_profile()
    
    def set_agent_profile(self) :
        self.id = self.set_id()
        self.consideration['risk_limit'] = np.random.randint(1, 100, 1) # 리스크 한도(Risk tolerance)
        self.consideration['investment_propensity'] = np.random.choice(['공격', '안정', '중립']) # 투자 성향
        self.consideration['balance'] = np.random.randint(500, 1000, 1) # 예산

    # 기본값 설정
    def set_id(self) :
        self.id = type(self)._counter
        type(self)._counter += 1
        return self.id

    # 투자자 행동
    def act(self) :
        print('투자자 행동')

        # 정보 탐색
        self.read_news()
                
        # 투자 집행
        self.do_investment()
        

    def read_news(self) :
        # 50% 확률로 생성된 뉴스를 읽음
        # 이후에 성향에 따라 모델링하는 방향 도입 (기관투자자가 더 잘 읽는다거나?)

        if np.random.random() > 0.5 :            
            print('뉴스를 읽습니다.')
            self.news = env.news
            self.consideration['news'] = self.news
        
        else :
            self.consideration['news'] = None


    def do_investment(self) :

        self.make_decision()

        if self.decision :  # 확대 또는 축소로 의사결정이 내려졌다면
            self.optimize_portfolio() # 포트폴리오 최적화하고,
            self.check_balance()      # 집행한 결과 반영


    def make_decision(self):
        print('고려할 사항 리스트 업...')
        print(self.consideration) 

        print('의사결정 내리는 중...')       
        self.decision = np.random.choice([1, -1, None]) # 1 : 확대, -1 : 축소, None : 중립

    def optimize_portfolio(self) :
        print('포트폴리오를 최적화 중...')

    def check_balance(self) :
        trade_fee = 10
        self.consideration['balance'] -= trade_fee


if __name__ == '__main__' :

    # 시뮬레이션 기본값 설정
    T = 10
    num_agent = 10

    # 환경 생성
    env = Environment()

    # 에이전트 생성
    agent = [Agent(env) for _ in range(num_agent)]

    # 시뮬레이션
    for t in range(T) :
        print()
        print(f"---------------- Stage {t} ----------------")

        # 환경 업데이트
        # 뉴스 생성 / 외부 shock
        env.generate_news()

        for i in range(num_agent) :
            agent[i].act()
                        
        # 환경 업데이트
        env.update()

        pdb.set_trace()