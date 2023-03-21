import pyupbit

access = "YxVrdqxu8DLAPibitVxoxRr7D9SRxGZxrgxJQ76f"          # 본인 값으로 변경
secret = "F2T3Z5CuuYv9JL7KdYTDVaxFrX3pLKneexlndw3W"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회