import datetime
import json
import upbit_call_module as up
import message_module as mp
import trade_module as tm
import time as t
import random
import traceback
import logging
import pandas as pd
from comn import comnQueryStrt, sqlTextBuilder, comnQueryWrk, comnQuerySel, comnQueryCls

# 전달받은 코인 리스트 업데이트
emergency_chk = 'Emergency drop'
user_call = False

def coin_receive_regular_selling():
    tm.trade_strt()
    global s_flag, simulate
    t_coin = None
    # while True:
    try:
        dt = datetime.datetime.now()
        conn, curs = comnQueryStrt() # SQL 서버 접속
        limit_flag = comnQuerySel(curs, conn,"SELECT * FROM trade_rules WHERE coin_key=1")[0] # 각 멀티 프로세스별 제한 상태 받아오기
        # trading_list = comnQuerySel(curs, conn,"SELECT * FROM trading_list WHERE coin_key=1")[0] # 각 멀티 프로세스별 접속 코인 리스트 받아오기
        sql_result = comnQuerySel(curs, conn,"SELECT c_code FROM coin_list_selling") # 판매 테이블에 있는 것만 따로 불러오기

        if len(sql_result) == 0: # 구매 완료된 코인이 없을 경우 5초 마다 확인
            return
            # continue
        
        s_flag = limit_flag['s_limit'] # 판매 제한 확인하기
        
        simulate = limit_flag['simulate']
        total_am = round(comnQuerySel(curs, conn,"SELECT or_am from deposit_holding WHERE coin_key=1")[0]['or_am'] * 0.88)

        for i in sql_result:
            try: t_coin = comnQuerySel(curs, conn,"SELECT * FROM coin_list_selling WHERE c_code='{}'".format(i['c_code']))[0] # DB에서 코인이름을 기준으로 직접 값을 불러오는 파트
            except: t_coin = None

            if t_coin != None:
                trade_factors, sma200, close_base = tm.get_all_factors(t_coin['c_code'], 15)
                strategy, case1, rsi_S = None, False, 'standby'
                if t_coin['record'] != 'NULL' and t_coin['record'] != None: 
                    t_coin['record'] = json.loads(t_coin['record'])
                    strategy = t_coin['record']['strategy']
                    try: case1 = t_coin['record']['case1_chk']
                    except: 
                        case1 = False
                    try: rsi_S = t_coin['record']['rsi_S']
                    except: 
                        rsi_S = 'standby'
                try:
                # 투자 전략 계산용 factor 받아오기
                    if trade_factors.iloc[-1]['rsi_K'] >= 80 and trade_factors.iloc[-1]['rsi_D'] >= 80:
                        case1 = True
                        rsi_S = 'ready'
                    else: 
                        case1 = False
                        if trade_factors.iloc[-1]['rsi_K'] < 90 and trade_factors.iloc[-1]['rsi_D'] < 80 and rsi_S == 'ready': 
                            rsi_S = 'go'
                except Exception as e:
                    logging.error("Exception 발생!")
                    logging.error(traceback.format_exc())
                    mp.post_message("#auto-trade", "{}: {}".format(t_coin['c_code'], e))
                    comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_coin['c_code'],'ERROR', json.dumps(t_coin['record']), """{}""".format(json.dumps(traceback.format_exc())),dt))
                    # continue
                    
                #RSI 지수 업데이트 {'c_code':item, 'position': "holding", 'rsi': None, 'record':c_ticker}
                t_coin['rsi'] = round(trade_factors.iloc[-1]['rsi'], 2)
                t_coin['record'] = {
                    'strategy': strategy,
                    'close': trade_factors.iloc[-1]['close'],
                    'MACD': round(trade_factors.iloc[-1]['macd'], 7),
                    'MACD_Signal': round(trade_factors.iloc[-1]['signal'], 7),
                    'rsi_K': round(trade_factors.iloc[-1]['rsi_K'], 2),
                    'rsi_D': round(trade_factors.iloc[-1]['rsi_D'], 2),
                    'case1_chk': case1,
                    'rsi_S': rsi_S
                    }
                up_chk_b = -0.05
                up_chk_b += ((trade_factors.iloc[-1]['close'] - t_coin['price_b']) / t_coin['price_b']) * 100
                t_coin['percent'] = up_chk_b
                if dt.minute % 1 == 0 and dt.second == 0:
                    mp.regular_percent_message(channel="#auto-trade",coin=t_coin['c_code'], percent=up_chk_b)
                user_call = comnQuerySel(curs, conn,"SELECT user_call FROM coin_holding WHERE c_code='{}'".format(t_coin['c_code']))[0]['user_call']
                if t_coin['hold'] == True and s_flag == False and str(t_coin['record']['strategy']).find('B') > -1:
                    try: t_coin = selling_process(c_list=trade_factors,sma200=sma200,t_record=t_coin, total_am=total_am, user_call=user_call, curs=curs,conn=conn)
                    except Exception as e:
                        logging.error("Exception 발생!")
                        logging.error(traceback.format_exc())
                        mp.post_message("#auto-trade", "{}: {}".format(t_coin['c_code'], e))
                        comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_coin['c_code'],'ERROR', json.dumps(t_coin['record']), """{}""".format(json.dumps(traceback.format_exc())),dt))
                        # continue
                sql_coin = t_coin
                sql_coin['record'] = json.dumps(t_coin['record']) # 거래기록을 DB에 저장
                
                if sql_coin['hold'] == True and str(t_coin['record']).find('B') > -1: 
                    comnQueryWrk(curs, conn,sqlText=sqlTextBuilder(li=sql_coin, table='coin_list_selling'))
                    t.sleep(0.01)
                    comnQueryWrk(curs, conn,"UPDATE coin_holding SET position='{}',rsi={}, current_price={}, current_percent={} WHERE c_code='{}'".format(
                        sql_coin['position'],sql_coin['rsi'],trade_factors.iloc[-1]['close'],up_chk_b,t_coin['c_code']))
                if sql_coin['hold'] == True and str(t_coin['record']).find('B') < 0 and t_coin['r_holding'] == 0: 
                    comnQueryWrk(curs, conn,"UPDATE coin_list SET hold=0,price_b=NULL,deposit=0,position='holding',buy_uuid='' WHERE c_code='{}'".format(t_coin['c_code']))
                    t.sleep(0.01)
                    comnQueryWrk(curs, conn,"DELETE FROM coin_list_selling WHERE c_code='{}'".format(t_coin['c_code'])) #판매 리스트에서 제거
                    t.sleep(0.01)
                    comnQueryWrk(curs, conn,"DELETE FROM coin_holding WHERE c_code='{}'".format(t_coin['c_code'])) #코인 보유 리스트에서 제거   
            del t_coin

    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt Exception 발생!")
        logging.error(traceback.format_exc())
        # 루프 안으로 exception check를 넣어서 문제가 5회 이상 발생시 긴급 판매 조치후 종료

    except Exception as e:
        logging.error("Exception 발생!")
        logging.error(traceback.format_exc())
        mp.post_message("#auto-trade", "{}: {}".format(t_coin['c_code'], e))
        comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_coin['c_code'],'ERROR', json.dumps(t_coin['record']), """{}""".format(json.dumps(traceback.format_exc())),dt))
    
    finally: 
        comnQueryCls(curs, conn)
        # continue

def coin_receive_user_selling():
    tm.trade_strt()
    global s_flag, simulate
    t_coin = None
    # while True:
    try:
        dt = datetime.datetime.now()
        conn, curs = comnQueryStrt() # SQL 서버 접속
        limit_flag = comnQuerySel(curs, conn,"SELECT * FROM trade_rules WHERE coin_key=1")[0] # 각 멀티 프로세스별 제한 상태 받아오기
        # trading_list = comnQuerySel(curs, conn,"SELECT * FROM trading_list WHERE coin_key=1")[0] # 각 멀티 프로세스별 접속 코인 리스트 받아오기
        sql_result = comnQuerySel(curs, conn,"SELECT c_code FROM coin_list_selling") # 판매 테이블에 있는 것만 따로 불러오기

        if len(sql_result) == 0: # 구매 완료된 코인이 없을 경우 5초 마다 확인
            return
            # continue
        
        s_flag = limit_flag['s_limit'] # 판매 제한 확인하기
        
        simulate = limit_flag['simulate']
        total_am = round(comnQuerySel(curs, conn,"SELECT or_am from deposit_holding WHERE coin_key=1")[0]['or_am'] * 0.88)

        for i in sql_result:
            try: t_coin = comnQuerySel(curs, conn,"SELECT * FROM coin_list_selling WHERE c_code='{}'".format(i['c_code']))[0] # DB에서 코인이름을 기준으로 직접 값을 불러오는 파트
            except: t_coin = None

            if t_coin != None:
                trade_factors, sma200, close_base = tm.get_all_factors(t_coin['c_code'], 15)
                strategy, case1, rsi_S = None, False, 'standby'
                if t_coin['record'] != 'NULL' and t_coin['record'] != None: 
                    t_coin['record'] = json.loads(t_coin['record'])
                    strategy = t_coin['record']['strategy']
                    try: case1 = t_coin['record']['case1_chk']
                    except: 
                        case1 = False
                    try: rsi_S = t_coin['record']['rsi_S']
                    except: 
                        rsi_S = 'standby'
                try:
                # 투자 전략 계산용 factor 받아오기
                    if trade_factors.iloc[-1]['rsi_K'] >= 80 and trade_factors.iloc[-1]['rsi_D'] >= 80:
                        case1 = True
                        rsi_S = 'ready'
                    else: 
                        case1 = False
                        if trade_factors.iloc[-1]['rsi_K'] < 90 and trade_factors.iloc[-1]['rsi_D'] < 80 and rsi_S == 'ready': 
                            rsi_S = 'go'
                except Exception as e:
                    logging.error("Exception 발생!")
                    logging.error(traceback.format_exc())
                    mp.post_message("#auto-trade", "{}: {}".format(t_coin['c_code'], e))
                    comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_coin['c_code'],'ERROR', json.dumps(t_coin['record']), """{}""".format(json.dumps(traceback.format_exc())),dt))
                    # continue
                    
                #RSI 지수 업데이트 {'c_code':item, 'position': "holding", 'rsi': None, 'record':c_ticker}
                t_coin['rsi'] = round(trade_factors.iloc[-1]['rsi'], 2)
                t_coin['record'] = {
                    'strategy': strategy,
                    'close': trade_factors.iloc[-1]['close'],
                    'MACD': round(trade_factors.iloc[-1]['macd'], 7),
                    'MACD_Signal': round(trade_factors.iloc[-1]['signal'], 7),
                    'rsi_K': round(trade_factors.iloc[-1]['rsi_K'], 2),
                    'rsi_D': round(trade_factors.iloc[-1]['rsi_D'], 2),
                    'case1_chk': case1,
                    'rsi_S': rsi_S
                    }
                up_chk_b = -0.05
                up_chk_b += ((trade_factors.iloc[-1]['close'] - t_coin['price_b']) / t_coin['price_b']) * 100
                t_coin['percent'] = up_chk_b
                if dt.minute % 1 == 0 and dt.second == 0:
                    mp.regular_percent_message(channel="#auto-trade",coin=t_coin['c_code'], percent=up_chk_b)
                user_call = comnQuerySel(curs, conn,"SELECT user_call FROM coin_holding WHERE c_code='{}'".format(t_coin['c_code']))[0]['user_call']
                if t_coin['hold'] == True and s_flag == False and str(t_coin['record']['strategy']).find('B') > -1 and user_call == 1:
                    try: t_coin = selling_process(c_list=trade_factors,sma200=sma200,t_record=t_coin, total_am=total_am, user_call=user_call, curs=curs,conn=conn)
                    except Exception as e:
                        logging.error("Exception 발생!")
                        logging.error(traceback.format_exc())
                        mp.post_message("#auto-trade", "{}: {}".format(t_coin['c_code'], e))
                        comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_coin['c_code'],'ERROR', json.dumps(t_coin['record']), """{}""".format(json.dumps(traceback.format_exc())),dt))
                        # continue
                sql_coin = t_coin
                sql_coin['record'] = json.dumps(t_coin['record']) # 거래기록을 DB에 저장
                
                if sql_coin['hold'] == True and str(t_coin['record']).find('B') > -1: 
                    comnQueryWrk(curs, conn,sqlText=sqlTextBuilder(li=sql_coin, table='coin_list_selling'))
                    t.sleep(0.01)
                    comnQueryWrk(curs, conn,"UPDATE coin_holding SET position='{}',rsi={}, current_price={}, current_percent={} WHERE c_code='{}'".format(
                        sql_coin['position'],sql_coin['rsi'],trade_factors.iloc[-1]['close'],up_chk_b,t_coin['c_code']))
                if sql_coin['hold'] == True and str(t_coin['record']).find('B') < 0 and t_coin['r_holding'] == 0: 
                    comnQueryWrk(curs, conn,"UPDATE coin_list SET hold=0,price_b=NULL,deposit=0,position='holding',buy_uuid='' WHERE c_code='{}'".format(t_coin['c_code']))
                    t.sleep(0.01)
                    comnQueryWrk(curs, conn,"DELETE FROM coin_list_selling WHERE c_code='{}'".format(t_coin['c_code'])) #판매 리스트에서 제거
                    t.sleep(0.01)
                    comnQueryWrk(curs, conn,"DELETE FROM coin_holding WHERE c_code='{}'".format(t_coin['c_code'])) #코인 보유 리스트에서 제거   
            del t_coin

    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt Exception 발생!")
        logging.error(traceback.format_exc())
        # 루프 안으로 exception check를 넣어서 문제가 5회 이상 발생시 긴급 판매 조치후 종료

    except Exception as e:
        logging.error("Exception 발생!")
        logging.error(traceback.format_exc())
        mp.post_message("#auto-trade", "{}: {}".format(t_coin['c_code'], e))
        comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_coin['c_code'],'ERROR', json.dumps(t_coin['record']), """{}""".format(json.dumps(traceback.format_exc())),dt))
    
    finally: 
        comnQueryCls(curs, conn)

def case1_check(trade_factors,sma200, case1_chk, up_chk_b, rsi_S, ubmi, ubmi_before): # 최상의 경우를 염두하고 작성한 케이스 1
    dt = datetime.datetime.now()
    checker = 1.5
    if ubmi - ubmi_before < -20: checker = 0.05
    if case1_chk == True and up_chk_b > checker and rsi_S == 'go' and dt.minute % 15 == 0:
        if trade_factors.iloc[-1]['signal'] > 0:
            if ((trade_factors.iloc[-1]['signal'] * 1.04) < trade_factors.iloc[-1]['macd'] < (trade_factors.iloc[-1]['signal'] * 3.5
                ) or (sma_check(trade_factors=sma200)== True and sma200.iloc[-1]['sma20'] > sma200.iloc[-1]['sma10'] * 1.03)): return True
        elif trade_factors.iloc[-1]['signal'] < 0:
            if (((trade_factors.iloc[-1]['signal'] * 0.965) < trade_factors.iloc[-1]['macd'] < 0) or (trade_factors.iloc[-1]['macd'] > 0
                ) or (sma_check(trade_factors=sma200)== True and sma200.iloc[-1]['sma20'] > sma200.iloc[-1]['sma10'] * 1.03)): return True
    return False

# 케이스2의 경우 많이 겹치는 부분이 많기 때문에 일정 퍼센트 이상 이익이 날 경우만 통과
def case2_check(trade_factors,sma200, up_chk_b, ubmi, ubmi_before): # 차상의 경우 혹은 몇몇 조건이 불충분한데 이익이 날 경우 
    dt = datetime.datetime.now()
    checker = 0.7
    if ubmi - ubmi_before < -20: checker = 0.05
    if up_chk_b > checker and trade_factors.iloc[-1]['signal'] > 0 and dt.minute % 15 == 0:
        if ((trade_factors.iloc[-1]['macd'] < (trade_factors.iloc[-1]['signal'] * 0.995) # MACD가 시그널 보다 낮은데 가격이 높을 경우
            ) or (trade_factors.iloc[-1]['rsi_K'] < (trade_factors.iloc[-1]['rsi_D'] - 5) # rsi_K 값이 rsi_D 값보다 낮은데 가격이 높을 경우
            ) or (sma_check(trade_factors=sma200)== False and (sma200.iloc[-1]['sma20'] * 0.95) > sma200.iloc[-1]['sma10'] # 이동평균선 20이 10보다 클 경우
            ) or ((trade_factors.iloc[-2]['high'] * 1.002) < trade_factors.iloc[-1]['close'] and (trade_factors.iloc[-1]['rsi_K'] < 75 and trade_factors.iloc[-1]['rsi_D'] < 55))
            # 저번 회차의 최대값보다 현재 값이 높은데 rsi_K 값이 75 이하 일 경우 
            ):
            return True
    elif up_chk_b > checker and trade_factors.iloc[-1]['signal'] < 0 and dt.minute % 15 == 0:
        if ((trade_factors.iloc[-1]['macd'] < (trade_factors.iloc[-1]['signal'] * 1.005)
            ) or (trade_factors.iloc[-1]['rsi_K'] < (trade_factors.iloc[-1]['rsi_D'] - 5)
            ) or (sma_check(trade_factors=sma200)== False and (sma200.iloc[-1]['sma20'] * 0.95) > sma200.iloc[-1]['sma10']
            ) or ((trade_factors.iloc[-2]['high'] * 1.002) < trade_factors.iloc[-1]['close'] and (
                trade_factors.iloc[-1]['rsi_K'] < 80 and trade_factors.iloc[-1]['rsi_D'] < 50))
            ): return True
    return False

def case3_check(trade_factors): # 케이스3의 경우 급락이 발생하여 확인 될 경우 발동
    p_up = (trade_factors.iloc[-2]['high'] - trade_factors.iloc[-2]['open']) / trade_factors.iloc[-2]['open'] * 100
    p_low = (trade_factors.iloc[-2]['low'] - trade_factors.iloc[-2]['open']) / trade_factors.iloc[-2]['open'] * 100
    candle = (trade_factors.iloc[-2]['close'] - trade_factors.iloc[-2]['open']) / trade_factors.iloc[-2]['open'] * 100
    p_up += (trade_factors.iloc[-1]['high'] - trade_factors.iloc[-1]['open']) / trade_factors.iloc[-1]['open'] * 100
    p_low += (trade_factors.iloc[-1]['low'] - trade_factors.iloc[-1]['open']) / trade_factors.iloc[-1]['open'] * 100
    candle += (trade_factors.iloc[-1]['close'] - trade_factors.iloc[-1]['open']) / trade_factors.iloc[-1]['open'] * 100
    if (p_up < 0.1 and p_low < -0.75 and candle < -0.8
        ) and (trade_factors.iloc[-2]['open'] > (trade_factors.iloc[-2]['close'] * 1.003)):
        return True 
    return False

def sma_check(trade_factors):
    ema20 = trade_factors.iloc[-1]['sma20']
    ema50 = trade_factors.iloc[-1]['sma50']
    ema100 = trade_factors.iloc[-1]['sma100']
    ema200 = trade_factors.iloc[-1]['sma200']
    if (ema200 * 1.005) < ema100 and  (ema100 * 1.005) < ema50 and (ema50 * 1.005) < ema20:
        return True
    return False

def add_to_blacklist(c_code, timeout, curs, conn):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "INSERT INTO blacklist (c_code, date, timeout) VALUES ('{}', '{}', {})".format(c_code, now, timeout)
    comnQueryWrk(curs=curs, conn=conn, sqlText=query)


def selling_process(c_list, t_record, sma200, total_am:float, user_call:bool, curs, conn): # 가지고 있는 코인 판매 가능 체크
    mes = ''
    dt = datetime.datetime.now()
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    global simulate, s_flag
    ubmi_data = comnQuerySel(curs, conn,"SELECT change_ubmi_now, change_ubmi_before FROM trading_list WHERE coin_key=1")[0]
    ubmi, ubmi_before = ubmi_data['change_ubmi_now'], ubmi_data['change_ubmi_before']
    total_profit = comnQuerySel(curs, conn,"SELECT (pr_am - (or_am * 0.12 - sv_am)) as pr_am FROM deposit_holding WHERE coin_key=1")[0]['pr_am'] # 수익금 확인
    if type(total_profit) != float or total_profit < 0: total_profit = 0
    cp = float(c_list.iloc[-1]['close'])
    up_chk_b = -0.05 # 전체 수익의 25% ~ 50%일 경우 긴급판매 발동  
    up_chk_b += ((float(cp) - t_record['price_b']) / t_record['price_b']) * 100
    info = {}
    # orderbook으로 구매 판매 조절 
    # Ask = 매도 호가 (판매 예약이 걸려있는 금액) 
    # Bid = 매수 호가 (구매 예약이 걸려있는 금액)
    # 만약 UBMI 지수가 -10 이하일 경우 limit_sell 를 써서 해당 가격에 판매 요청을 한다, 
    # 포지션이 selling 일 경우 오더 채크로 해당 주문이 완료 되었는지 확인한다. 
    case1_chk, case2_chk, case3_chk = False, False, False
    if (case1_check(trade_factors=c_list, sma200=sma200, ubmi=ubmi, ubmi_before=ubmi_before, case1_chk=t_record['record']['case1_chk'], up_chk_b=up_chk_b, rsi_S=[t_record['record']['rsi_S']]) == True and (t_record['hold'] == True and case2_chk == False and case3_chk == False)): 
        case1_chk, t_record['position'] = True, 'reach profit point case 1'
    if (case2_check(trade_factors=c_list, sma200=sma200, ubmi=ubmi, ubmi_before=ubmi_before, up_chk_b=up_chk_b) == True and (t_record['hold'] == True and case1_chk == False and case3_chk == False)):
        case2_chk, t_record['position'] = True, 'reach profit point case 2'
    if (case3_check(trade_factors=c_list) == True and (t_record['hold'] == True and case2_chk == False and case1_chk == False)):
        if up_chk_b > 0.05: 
            t_record['position'] = 'reach profit point case 3'
        elif up_chk_b < -0.75: 
            t_record['position'] = 'emergency case 3'
        case3_chk = True
    if t_record['r_holding'] == 0 and simulate == False: 'emergency real coin sold'
    if c_list.iloc[-1]['signal'] > 0:
        if (c_list.iloc[-1]['macd'] <= (c_list.iloc[-1]['signal'] * 0.95)
            ) and (t_record['hold'] == True
            ) and (up_chk_b < -0.7): 
            t_record['position'] = 'emergency 1 -0.7% check'
    if c_list.iloc[-1]['signal'] < 0:
        if (c_list.iloc[-1]['macd'] <= (c_list.iloc[-1]['signal'] * 1.05)
            ) and (t_record['hold'] == True
            ) and (up_chk_b < -0.75): 
            t_record['position'] = 'emergency 2 -0.7% check'
    if sma200.iloc[-1]['sma10'] < sma200.iloc[-1]['sma20'] and sma_check(trade_factors=sma200) == False and (up_chk_b < -2.95): 
        t_record['position'] = 'emergency 3 sudden drop' # 갑작스럽게 내릴 경우 1
        
    # if (change_ubmi_before != None and (change_ubmi_now - change_ubmi_before) < -80 and dt.hour != 9 and change_ubmi_now < -50): # UBMI 지수가 저번 지수보다 -80 이상 갑자기 급락하고 현재 지수가 -50 이하일 경우
    #     if up_chk_b > 0.05: t_record['position'] = 'reach profit point 4 UBMI drop -80'
    #     else: t_record['position'] = 'emergency 4 UBMI drop -80'
    checker = 0.5
    if ubmi < -50: checker = 0.05
    elif ubmi > 50: checker = 0.8
    elif ubmi - ubmi_before < -20: checker = 0.05
    
    if up_chk_b < -0.95 and ubmi - ubmi_before < -20 and (str(t_record['position']).find('emergency') == -1 or str(t_record['position']).find('reach profit point') == -1): 
        t_record['position'] = 'emergency 5 -1% check'
    if up_chk_b > checker and ubmi - ubmi_before < -20 and (str(t_record['position']).find('emergency') == -1 or str(t_record['position']).find('reach profit point') == -1): 
        t_record['position'] = 'emergency 6 {}% check'.format(checker)
    info = {
        'sell_uuid': '', 
        'volume': 0,
        'side': 'ask',
        'state': 'wait'
        }
    if (str(t_record['position']).find('emergency') > -1 or str(t_record['position']).find('reach profit point') > -1): 
        info['state'] = 'done'

    if (str(t_record['position']).find('emergency') > -1 or str(t_record['position']).find('reach profit point') > -1) or user_call == True:
        try:    
            if s_flag == False: 
                info = {}
                if simulate == False and t_record['r_holding'] == True and t_record['sell_uuid'] == '': # 시뮬레이션이 아닐때 
                    if (str(t_record['position']).find('reach profit point') > -1):
                        info = tm.limit_call_sell(coin=t_record['c_code'], price=cp, volume=t_record['volume'])
                    elif (str(t_record['position']).find('emergency') > -1):
                        info = tm.trade_call_sell(coin=t_record['c_code'], volume=t_record['volume'])
                    t_record['sell_uuid'] = info['uuid']  
                    comnQueryWrk(curs, conn,"UPDATE coin_list_selling SET sell_uuid='{}' WHERE c_code='{}'".format(info['uuid'], t_record['c_code']))
                elif simulate == True and t_record['r_holding'] == False: 
                    info['state'] = 'cancelled'
                    info['volume'] = 0
        except Exception as e:
            logging.error("Exception 발생!")
            logging.error(traceback.format_exc())
            mp.post_message("#auto-trade", "{}: {}, {}".format(t_record['c_code'], e, info))
            comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_record['c_code'],'ERROR', '', """{}""".format(traceback.format_exc()),dt))
            info = None
        if info != None:
            try: cp = float(info['trades'][0]['price'])
            except: cp = c_list.iloc[-1]['close']
            # if ((info != None or simulate == True) and t_record['position'] == 'holding') or t_record['sell_uuid'] == 'canceled':
            up_chk_b = -0.05 # 전체 수익의 25% ~ 50%일 경우 긴급판매 발동  
            up_chk_b += ((float(cp) - t_record['price_b']) / t_record['price_b']) * 100
            # 수익 소수점 반올림
            deposit = round(t_record['deposit'] + (t_record['deposit'] * (up_chk_b/100)))
            op = round(total_am)
            remain = op % 22
            op -= remain
            op = op / 22
            # 판매 메세지 변경
            if str(t_record['position']).find('reach profit point') > -1: mes="매도 고점 도달"
            elif str(t_record['position']).find('emergency') > -1: 
                if up_chk_b < 0:
                    # 여기 블랙리스트 추가 Ex: {"c_code": "KRW-BTC", "date":"2024-10-03 08:51:30"} 
                    # 블랙리스트의 date 비교 하는 코드를 새로 추가하여 15분 지나면 블랙리스트에서 삭제하는 코드 생성
                    add_to_blacklist(t_record['c_code'], 15, curs, conn)
                    mes = "매도 저점 도달"
                elif up_chk_b > 0:
                    # 여기 블랙리스트 추가 Ex: {"c_code": "KRW-BTC", "date":"2024-10-03 08:51:30"} 
                    # 블랙리스트의 date 비교 하는 코드를 새로 추가하여 2분 지나면 블랙리스트에서 삭제하는 코드 생성
                    add_to_blacklist(t_record['c_code'], 2, curs, conn)
                    mes = "매도 고점 도달"
            elif user_call == True: mes = "User ask for Sell" # 사용자 신청
            else: mes = '이상 발생'
            
            if (user_call == 1 or str(t_record['position']).find('emergency') > -1 or str(t_record['position']).find('reach profit point') > -1):
                if case1_chk == True: t_record['record']['strategy'] = 'case 1 S ' + t_record['record']['strategy']
                elif case2_chk == True: t_record['record']['strategy'] = 'case 2 S '+ t_record['record']['strategy']
                elif case3_chk == True: t_record['record']['strategy'] = 'case 3 S '+ t_record['record']['strategy']
                elif user_call == False and str(t_record['position']).find('emergency') > -1: t_record['record']['strategy'] = 'case E S ' + t_record['record']['strategy']
                elif user_call == True: t_record['record']['strategy'] = 'case U S ' + t_record['record']['strategy']

                #이익금 정리
                if str(t_record['position']).find('emergency') > -1:
                    report = "c_code: " + t_record['c_code'] +"\nposition: " + t_record['position'] +"\nprocess: SELL"+"\ncurrent price: "+str(cp) + "\n손절 포인트 도달\n급매도 요청 발생"
                elif str(t_record['position']).find('reach profit point') > -1:
                    report = "c_code: " + t_record['c_code'] +"\nposition: " + t_record['position'] +"\nprocess: SELL"+"\ncurrent price: "+str(cp) + "\n익절 포인트 도달\n급매도 요청 발생"
                elif user_call == True: report = "c_code: " + t_record['c_code'] +"\nprocess: SELL"+"\ncurrent price: "+str(cp) + "\n사용자 요청 발생\n급매도 요청 발생"
                mp.post_message("#auto-trade", report) #Slack에 메세지 전송
                comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_record['c_code'],'SELL', json.dumps(t_record['record']), report,dt))
                tm.profit_control(total_am=total_am,deposit=deposit) 
                per_deal = format(up_chk_b, ".3f")
                message = "c_code: " + t_record['c_code'] +"\nprocess: SELL"+"\nprice_b: "+ str(t_record['price_b'])+"\nprice_s: "+str(cp)+ "\ndate_time: " + str(dt_str) +"\nStrategy: "+ str(t_record['record']['strategy']) + "\nresult: {}%, W {}".format(per_deal, deposit)+"\nSOLD: {}".format(mes)
                
                mp.post_message("#auto-trade", message) #Slack에 메세지 전송
                # 결과 DB 전송 
                lst={'c_code': t_record['c_code'], 'c_rank':int(t_record['record']['strategy'][-1]), 'current_price': cp, 'percent': per_deal, 'date_time':dt, 'c_status': 'SOLD: {}'.format(t_record['record']['strategy']), 'reason': mes, 'deposit': deposit}
                comnQueryWrk(curs, conn,sqlTextBuilder(li=lst,table='trade_history')) #거래 기록 추가
                
                comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_record['c_code'],'SELL', json.dumps(t_record['record']), message,dt))
                t_record['hold'] = False # 판매 완료후 설정 변경 
                t_record['position'] = 'holding'
                t_record['sell_uuid'] = ''
                t_record['price_b'] = None
                t_record['deposit'] = 0
                comnQueryWrk(curs, conn,"UPDATE coin_list SET hold=0,price_b=NULL,deposit=0,position='holding',buy_uuid='' WHERE c_code='{}'".format(t_record['c_code']))
                t.sleep(0.01)
                comnQueryWrk(curs, conn,"DELETE FROM coin_list_selling WHERE c_code='{}'".format(t_record['c_code'])) #판매 리스트에서 제거
                t.sleep(0.01)
                comnQueryWrk(curs, conn,"DELETE FROM coin_holding WHERE c_code='{}'".format(t_record['c_code'])) #코인 보유 리스트에서 제거   
    return t_record
        # 판매 완료 대기중, 현재가가 지정된 전저가 이하로 내려갈 경우, 사용자 판매 요청이 있을 경우
        # print("info['state'] != wait 확인후 주문 상태 조회후 판매 완료 되었을 경우")
        # print("코인 상태 업데이트 및 메세지 전달")
