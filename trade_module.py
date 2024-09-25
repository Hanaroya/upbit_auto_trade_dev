import hashlib
import json
import time
import uuid
import jwt
import pandas as pd
import pyupbit as upbit
import upbit_call_module as uc
import requests
import get_properties as gp
import requests
from urllib.parse import urlencode, unquote
from comn import comnQueryCls, comnQueryStrt, comnQueryWrk, comnQuerySel
import numpy as np

myprops = gp.get_properties()
access = myprops['UPBIT_ACCESS'] # 업비트 Access 키
secret = myprops['UPBIT_SECRET'] # 업비트 Secret 키
server_url = 'https://api.upbit.com'

def trade_strt():
    global up
    up = upbit.Upbit(access, secret)

def trade_call_buy(coin:str, amt:float): # 구매 확인 스캐쥴을 만들어 루프 제거
    global up
    if up.get_balance() == 0: return None
    ret = up.buy_market_order(coin, amt)
    
    # {'uuid': '53d51388-1c7d-4d02-9bdd-b4ef28644b71', 'side': 'ask', 'ord_type': 'market', 'state': 'wait', 'market': 'KRW-XRP', 
    # 'created_at': '2023-06-07T11:02:28.043371+09:00', 'volume': '11.52161383', 'remaining_volume': '11.52161383', 'reserved_fee': '0', 
    # 'remaining_fee': '0', 'paid_fee': '0', 'locked': '11.52161383', 'executed_volume': '0', 'trades_count': 0} 결과 예시
    return ret

def trade_call_sell(coin:str, volume): # 판매 확인 스캐쥴을 만들어 루프 제거
    global up
    if up.get_balance(coin) == 0: return None
    ret = up.sell_market_order(coin, volume)
    
    # {'uuid': '53d51388-1c7d-4d02-9bdd-b4ef28644b71', 'side': 'ask', 'ord_type': 'market', 'state': 'wait', 'market': 'KRW-XRP', 
    # 'created_at': '2023-06-07T11:02:28.043371+09:00', 'volume': '11.52161383', 'remaining_volume': '11.52161383', 'reserved_fee': '0', 
    # 'remaining_fee': '0', 'paid_fee': '0', 'locked': '11.52161383', 'executed_volume': '0', 'trades_count': 0} 결과 예시
    return ret

def limit_call_buy(coin:str,price:float,amt:float):
    global up
    ret = up.buy_limit_order(ticker=coin, price=price, volume=(amt/price))
    
    return ret

def limit_call_sell(coin:str,price:float,volume:float):
    global up
    if up.get_balance(coin) == 0: return None
    ret = up.sell_limit_order(ticker=coin,price=price,volume=volume)
    return ret
# -----------------------------------------------------------------------------
# - Name : cancel_order_uuid
# - Desc : 미체결 주문 취소 by UUID
# - Input
#   1) order_uuid : 주문 키
# - Output
#   1) 주문 내역 취소
# -----------------------------------------------------------------------------
def cancel_order_uuid(order_uuid):
    try:
 
        query = {
            'uuid': order_uuid,
        }
 
        query_string = urlencode(query).encode()
 
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()
 
        payload = {
            'access_key': myprops['UPBIT_ACCESS'],
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }
 
        jwt_token = jwt.encode(payload, myprops['UPBIT_SECRET'])
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}
 
        res = uc.send_request("DELETE", server_url + "/v1/order", query, headers)
        rtn_data = res.json()
 
        return rtn_data
 
    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise

# -----------------------------------------------------------------------------
# - Name : cancel_order
# - Desc : 미체결 주문 취소
# - Input
#   1) target_item : 대상종목
#   2) side : 매수/매도 구분(BUY/bid:매수, SELL/ask:매도, ALL:전체)
# - Output
# -----------------------------------------------------------------------------
def cancel_order(target_item, side):
    try:
        global up
        # 미체결 주문 조회
        order_data = up.get_order(target_item)
 
        # 매수/매도 구분
        for order_data_for in order_data:
 
            if side == "BUY" or side == "buy":
                if order_data_for['side'] == "ask":
                    order_data.remove(order_data_for)
            elif side == "SELL" or side == "sell":
                if order_data_for['side'] == "bid":
                    order_data.remove(order_data_for)
 
        # 미체결 주문이 있으면
        if len(order_data) > 0:
 
            # 미체결 주문내역 전체 취소
            for order_data_for in order_data:
                cancel_order_uuid(order_data_for['uuid'])
 
    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise
def get_market_orders(coin:str):
    params = {
        'states[]': ['done', 'cancel'],
        'market': coin,
    }
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': myprops['UPBIT_ACCESS'],
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, myprops['UPBIT_SECRET'])
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {'Authorization': authorization}

    res = requests.get(server_url + '/v1/orders', params=params, headers=headers)
    return res.json()
    

def get_balance(coin:str):
    global up
    return up.get_balance(coin)

def get_balances():
    u = upbit.Upbit(access, secret)
    return u.get_balances()


def orders_status(orderid):
    query = {
        'uuid': f'{orderid}',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': myprops['UPBIT_ACCESS'],
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload,  myprops['UPBIT_SECRET'])
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/order", params=query, headers=headers)
    # {'uuid': '53d51388-1c7d-4d02-9bdd-b4ef28644b71', 'side': 'ask', 'ord_type': 'market', 'state': 'done', 'market': 'KRW-XRP', 
    # 'created_at': '2023-06-07T11:02:28+09:00', 'volume': '11.52161383', 'remaining_volume': '0', 'reserved_fee': '0', 'remaining_fee': '0', 
    # 'paid_fee': '3.98647838518', 'locked': '0', 'executed_volume': '11.52161383', 'trades_count': 1, 
    # 'trades': [{'market': 'KRW-XRP', 'uuid': '41961874-df86-495f-bb9e-9555d4ce6b47', 'price': '692', 'volume': '11.52161383', 'funds': '7972.95677036', 
    # 'trend': 'down', 'created_at': '2023-06-07T11:02:28+09:00', 'side': 'ask'}]} 결과 예시

    return res.json()


def profit_control(total_am:float, deposit:float):
    dep = round(total_am/8) 
    dep_chk = round(deposit - dep) # 실제 평가 금액 확인 
    conn, curs = comnQueryStrt()
    sv_chk = comnQuerySel(curs, conn, "SELECT sv_am FROM deposit_holding WHERE coin_key=1")[0]['sv_am'] # sv_am 보험용 전체 금액의 12% 체크
    remain = round(comnQuerySel(curs, conn, "SELECT or_am FROM deposit_holding WHERE coin_key=1")[0]['or_am'] * 0.88) % 8
    sv_or = round(comnQuerySel(curs, conn, "SELECT or_am FROM deposit_holding WHERE coin_key=1")[0]['or_am'] * 0.12) + remain
    comnQueryWrk(curs, conn, "UPDATE deposit_holding SET dp_am = dp_am + {} WHERE coin_key=1".format(dep)) # 1. 거래 금액 8% 원상복귀

    # 2. 이익금이 마이너스일 경우 이익금의 마이너스 분량만큼 보험금액에서 빼기
    if dep_chk < 0: comnQueryWrk(curs, conn, "UPDATE deposit_holding SET pr_am = pr_am + ({}) WHERE coin_key=1".format(dep_chk))
    else: # 3. 이익금이 플러스일 경우 
        if sv_chk - sv_or >= 0: # 3-1. 저축 분량 체크 만약 보험금액에 전체의 12% 이상이거나 딱 12%일때
            if sv_chk == sv_or: comnQueryWrk(curs, conn, "UPDATE deposit_holding SET pr_am = pr_am + {} WHERE coin_key=1".format(dep_chk)) # 3-2. 딱 12% 충족시 이익금에 추가 
            if sv_chk - sv_or > 0: # 3-3. 12% 이상일시 추가분 profit에 넣고 원상복귀 
                comnQueryWrk(curs, conn, "UPDATE deposit_holding SET pr_am = pr_am + {} WHERE coin_key=1".format(sv_chk - sv_or))
                comnQueryWrk(curs, conn, "UPDATE deposit_holding SET sv_am = {} WHERE coin_key=1".format(sv_or))
        else: # 4. 보험금이 전체금액의 12% 미만일 경우 
            sv = sv_chk + dep_chk
            if sv > sv_or: # 4-1. 현재 보험용 금액 + 이익금 > 전체금액의 12% 보다 클 경우 
                comnQueryWrk(curs, conn, "UPDATE deposit_holding SET sv_am = {} WHERE coin_key=1".format(sv_or)) # 12% 금액으로 원상복귀
                comnQueryWrk(curs, conn, "UPDATE deposit_holding SET pr_am = pr_am + {} WHERE coin_key=1".format(sv - sv_or)) # 남은 금액 이익금에 추가
            else: comnQueryWrk(curs, conn, "UPDATE deposit_holding SET sv_am = sv_am + {} WHERE coin_key=1".format(dep_chk)) # 5. 이익금 + 현재 보험금이 전체 12% 미만일 경우 이익금 현재 보험금에 추가 
    comnQueryCls(curs, conn)
    
def get_prices(orderbook:dict, cp:float):
    items = orderbook['orderbook_units']
    price_l = None # 실거래시 물타기 제대로 작동 안해서 추가
    price_h = None
    for i in range(len(items)):
        up_chk_b = -0.05 # 전체 수익의 25% ~ 50%일 경우 긴급판매 발동  
        up_chk_b += ((items[i]['ask_price'] - float(cp)) / float(cp)) * 100
        if items[i]['ask_price'] > cp and up_chk_b > 0.05 and price_h == None: 
            price_h = items[i]['ask_price']
        if items[i]['bid_price'] < cp and price_l == None: 
            price_l = items[i]['bid_price']
    if price_l == None: price_l = orderbook['orderbook_units'][-1]['bid_price']
    if price_h == None: price_h = orderbook['orderbook_units'][-1]['ask_price']
    return {'price_low':price_l, 'price_high':price_h}

def get_orderbook(coin:str):
    url = "https://api.upbit.com/v1/orderbook?markets={}".format(coin)
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    return json.loads(response.text)

    # 스토케스틱 RSI 구하는 매소드 https://www.youtube.com/watch?v=_-uLIYz9O4g&list=PLX-N_N-UxWBblXQVQIJc9wir3ZN5p9og9&index=5&t=37s&pp=gAQBiAQB
    # https://www.youtube.com/watch?v=jYU_or14VTk&list=PLX-N_N-UxWBblXQVQIJc9wir3ZN5p9og9&index=3&t=63s&pp=gAQBiAQB
    # https://www.youtube.com/watch?v=H0E4_5iK3pQ&list=PLX-N_N-UxWBblXQVQIJc9wir3ZN5p9og9&index=4&t=138s&pp=gAQBiAQB                        
    # Fast %K 계산

def get_stochastic_oscillator(df, n=14, d_n=3):
    # 스토캐스틱 계산
    df['Lowest_N_Minutes'] = df['low'].rolling(window=n).min()
    df['Highest_N_Minutes'] = df['high'].rolling(window=n).max()
    df['rsi_K'] = (df['close'] - df['Lowest_N_Minutes']) / (df['Highest_N_Minutes'] - df['Lowest_N_Minutes']) * 100
    df['rsi_D'] = df['rsi_K'].rolling(window=d_n).mean()
    delta = df['close'].diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[n-1]] = np.mean( ups[:n] )
    ups = ups.drop(ups.index[:(n-1)])
    downs[downs.index[n-1]] = np.mean( downs[:n] )
    downs = downs.drop(downs.index[:(n-1)])
    rs = ups.ewm(com=n-1,min_periods=0,adjust=False,ignore_na=False).mean() / \
         downs.ewm(com=n-1,min_periods=0,adjust=False,ignore_na=False).mean() 
    rsi = 100 - 100 / (1 + rs)
    df['rsi'] = rsi
    
    stochrsi  = (rsi - rsi.rolling(n).min()) / (rsi.rolling(n).max() - rsi.rolling(n).min()) * 100
    df['rsi_K'] = stochrsi.rolling(d_n).mean()
    df['rsi_D'] = df['rsi_K'].rolling(d_n).mean()
    
    # 결과 반환
    return df

def calculate_sma(df): # 200일 이동 평균선 구하는 메소드
    df['sma5'] = df['close'].rolling(5).mean()
    df['sma10'] = df['close'].rolling(10).mean()
    df['sma20'] = df['close'].rolling(20).mean()
    df['sma30'] = df['close'].rolling(30).mean()
    df['sma50'] = df['close'].rolling(50).mean()
    df['sma100'] = df['close'].rolling(100).mean()
    df['sma200'] = df['close'].rolling(200).mean()
    return df

def calculate_volume_ma(df): # 200일 이동 평균선 구하는 메소드
    df['volume5'] = df['volume'].rolling(5).mean()
    df['volume20'] = df['volume'].rolling(20).mean()
    df['volume30'] = df['volume'].rolling(30).mean()
    df['volume100'] = df['volume'].rolling(100).mean()
    return df

# 지수이동평균 (Exponential Moving Average)
def calculate_ema(df, length):
    df['ema'] = df['close'].ewm(span=length, adjust=False).mean()
    return df

def calculate_bollinger_bands(df, window=20, num_of_std=2):
    # 이동평균선 계산
    df['sma'] = df['close'].rolling(window=window).mean()

    # 이동평균선 기준으로 표준편차 계산
    std = df['close'].rolling(window=window).std()

    # 볼린저 밴드 계산
    df['upper_band'] = df['sma'] + num_of_std * std
    df['lower_band'] = df['sma'] - num_of_std * std

    return df

def double_bollinger_bands(df, window=20, inner_std=0.5, outer_std=3):
    # 이동평균선 계산
    df['sma'] = df['close'].rolling(window=window).mean()

    # 이동평균선 기준으로 표준편차 계산
    std = df['close'].rolling(window=window).std()

    # 안쪽 볼린저 밴드 계산
    df['inner_upper_band'] = df['sma'] + inner_std * std
    df['inner_lower_band'] = df['sma'] - inner_std * std
    
    # 바깥쪽 볼린저 밴드 계산
    df['outer_upper_band'] = df['sma'] + outer_std * std
    df['outer_lower_band'] = df['sma'] - outer_std * std

    return df
    # https://www.youtube.com/watch?v=EGQPqccVKZk&list=PLX-N_N-UxWBblXQVQIJc9wir3ZN5p9og9&index=10&pp=gAQBiAQB

def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    # 단기 이동평균선 (Fast EMA) 계산
    df['fast_ema'] = df['close'].ewm(span=fast_period, adjust=False).mean()

    # 장기 이동평균선 (Slow EMA) 계산
    df['slow_ema'] = df['close'].ewm(span=slow_period, adjust=False).mean()

    # MACD Line 계산
    df['macd'] = df['fast_ema'] - df['slow_ema']

    # Signal Line 계산
    df['signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()

    # MACD Oscillator 계산
    df['oscillator'] = df['macd'] - df['signal']

    return df

# 최대 최소값
def recent_max(source, length):
    return source.rolling(window=length).max()

def recent_min(source, length, cp):
    result = source.rolling(window=length).min()
    check_leng = length
    try: 
        while result == cp:
            result = source.rolling(window=check_leng).min()
            check_leng += 10
    except: return cp
    return result

def get_all_factors(coin, min):
    try: data = list(reversed(uc.total_price_calls(input_idx=coin, min=min)))
    except: return None
    # data_200_days = reversed(uc.total_200_days_call(coin))
    df = pd.DataFrame({'list': data})
    # df_200 = pd.DataFrame({'list': data_200_days})
    sma200 = pd.DataFrame({'close': [d.get('tradePrice') for d in df['list']]})
    volume_base = [d.get('candleAccTradeVolume') for d in df['list']]
    close_base = [d.get('tradePrice') for d in df['list']]
    date_base = pd.DatetimeIndex([d.get('candleDateTimeKst') for d in df['list']])
    open_base = [d.get('openingPrice') for d in df['list']]
    highPrice_base = [d.get('highPrice') for d in df['list']]
    lowPrice_base = [d.get('lowPrice') for d in df['list']]
    
    try:
        trade_factors = pd.DataFrame({'close': close_base, 'open': open_base, 'high': highPrice_base, 'low': lowPrice_base, 'volume': volume_base, 'date': date_base})
        trade_factors = get_stochastic_oscillator(trade_factors) # 스토케스틱 RSI 지수 계산
        trade_factors = calculate_bollinger_bands(trade_factors) # 볼린저밴드 지수 계산
        trade_factors = double_bollinger_bands(trade_factors) # 더블 볼린저밴드 지수 계산
        trade_factors = calculate_macd(trade_factors) # MACD 지수 계산
        trade_factors = calculate_volume_ma(trade_factors) # MACD 지수 계산
        sma200 = calculate_sma(sma200) # 200일 이동 평균선 계산
    except: 
        pass 
    finally:
        return trade_factors.iloc[-200:], sma200.iloc[-200:], close_base[-200:]

def get_price(orderbook, position ,cp):
    for i in orderbook['orderbook_units']:
        if position == 'ask_price':
            up_chk_b = -0.05
            up_chk_b += ((i['ask_price'] - cp) / cp) * 100
            if cp < i['ask_price']:
                return i['ask_price']
            if i == orderbook['orderbook_units'][-1] and up_chk_b < 0.05:
                return round(cp + (cp * 0.0006), 1)
        elif position == 'bid_price':
            if cp > i['bid_price']:
                return i['bid_price']
    return orderbook['orderbook_units'][0][position]
            