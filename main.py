import pdb
import numpy as np

class Environment() :
    def __init__(self):
        self.interest_rate = 1.0
        self.news = ""

    def update(self) :
        self.interest_rate += np.random.random()

    def publish_news(self) :
        self.news = f"뉴스 {round(np.random.random(), 2)}"

    def stock(self) :
        pass

class Agent() :
    _counter = 0        

    def __init__(self, env:Environment):
        self.env = env
        self.set_agent_profile()
    
    def set_agent_profile(self) :
        self.id = self.set_id()
        self.risk_tolerance = np.random.randint(1, 100, 1)
        self.investment_propensity = np.random.choice(['공격', '안정', '중립'])

    # 기본값 설정
    def set_id(self) :
        self.id = type(self)._counter
        type(self)._counter += 1
        return self.id

    # 투자자 행동
    def do_investment(self) :
        # 뉴스 읽기
        self.news = self.read_news()

    def read_news(self) :
        # 50% 확률로 생성된 뉴스를 읽음
        if np.random.random() > 0.5 :
            return env.news
        else :
            return None

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
        env.publish_news()
        print(f"뉴스 생성 : {env.news}")

        for i in range(num_agent) :
            agent[i].do_investment()
            print(f"ID : {agent[i].id} | NEWS : {agent[i].news} | ENVIRONMENT : {agent[i].env.interest_rate}")
                        
        # 환경 업데이트
        env.update()

    pdb.set_trace()