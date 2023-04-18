import time
import pyupbit
import datetime
import numpy as np

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-XRP", count = 7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_optimal_k():
    max_ror = -np.inf
    optimal_k = 0.1
    
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        
        if ror > max_ror:
            max_ror = ror
            optimal_k = k
            
    return optimal_k

# 로그인
with open("api_key.txt") as f:
    lines = f.readlines()
    access = lines[0].strip()
    secret = lines[1].strip()
    upbit = pyupbit.Upbit(access, secret)
    print("autotrade start")

# 초기값 설정
investment = get_balance("KRW") * 0.01 # 초기 투자 금액
shares = investment / get_current_price("KRW-XRP")  # 초기 주식 수
price = get_current_price("KRW-XRP")  # 초기 주식 가격
losses = 0  # 초기 손실 금액

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(days=1)

        # 주식 매수
        investment = investment + losses  # 이전 거래에서 발생한 손실을 더함
        shares_to_buy = investment / price  # 주식 매수 수량 계산
        shares += shares_to_buy  # 주식 수량 추가
        investment = shares * price  # 새로운 투자 금액 계산
        print('Bought', shares_to_buy, 'shares at', price, 'per share')
        
        # 주식 가격 변동 시뮬레이션
        price_change = get_current_price("KRW-XRP") - price  # 가격 변동 계산
        price = get_current_price("KRW-XRP")  # 가격 업데이트
        investment = shares * price  # 투자 금액 업데이트

        # 이익 또는 손실 계산
        if price_change > 0:
            print('Profit of', price_change * shares, 'on this trade')
            losses = 0  # 손실 초기화
        else:
            print('Loss of', price_change * shares, 'on this trade')
            losses = investment * 2  # 이전 거래에서 발생한 손실의 두 배를 다음 거래에서 투자

        # 거래 중단 조건
        if investment <= 0:
            print('Investment depleted. Exiting trading.')
            break

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-XRP", get_optimal_k)
            current_price = get_current_price("KRW-XRP")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 40000:
                    upbit.buy_market_order("KRW-XRP", krw*0.9995)
        else:
            xrp = get_balance("XRP")
            if xrp > 0.00008:
                upbit.sell_market_order("KRW-XRP", xrp*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)