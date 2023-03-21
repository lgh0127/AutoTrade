import pyupbit
import numpy as np


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

for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))

optimal_k = get_optimal_k()
print("Optimal k value:", optimal_k)