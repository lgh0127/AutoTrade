import time
import pyupbit
import datetime
import numpy as np

access = "YxVrdqxu8DLAPibitVxoxRr7D9SRxGZxrgxJQ76f"
secret = "F2T3Z5CuuYv9JL7KdYTDVaxFrX3pLKneexlndw3W"

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

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

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
    """최적 K값 산출"""
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
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(days=1)     

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-XRP", get_optimal_k())
            ma15 = get_ma15("KRW-XRP")
            current_price = get_current_price("KRW-XRP")
            krw = get_balance("KRW")

            print("Program is Running...")
            print("Target Price =",target_price)
            print("Ma15 =",ma15)
            print("Current Price =",current_price)
            print("Balance = ",krw)
            
            if target_price < current_price and ma15 < current_price:               
                if krw > 40000:
                    upbit.buy_market_order("KRW-XRP", krw*0.1995)
        else:
            xrp = get_balance("XRP")
            if xrp > 0:
                upbit.sell_market_order("KRW-XRP", xrp*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)