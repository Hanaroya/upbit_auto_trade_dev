import datetime
import json
import upbit_call_module as up
import message_module as mp
import trade_module as tm
import time as t
import traceback
import logging

from comn import comnQueryStrt, sqlTextBuilder, comnQueryWrk, comnQuerySel, comnQueryCls

# 전달받은 코인 리스트 업데이트
user_call = False
checking = ['buying', 'checking', 'cancel']

def coin_receive_buying(c_rank):
    tm.trade_strt()
    global b_flag, simulate
    t_coin = None
    idx = 0
    # while True:
    try:
        now = datetime.datetime.now()
        conn, curs = comnQueryStrt() # SQL 서버 접속
        trading_list = comnQuerySel(curs, conn,"SELECT * FROM trading_list WHERE coin_key=1")[0] # 각 멀티 프로세스별 접속 코인 리스트 받아오기
        limit_flag = comnQuerySel(curs, conn,"SELECT * FROM trade_rules WHERE coin_key=1")[0] # 각 멀티 프로세스별 제한 상태 받아오기
        coin_list = json.loads(trading_list['coin_pl'])
        
        # 블랙리스트 호출
        blacklist = comnQuerySel(curs, conn, "SELECT c_code FROM blacklist WHERE timeout > 0 and out_count < 3")
        blacklist_codes = [item['c_code'] for item in blacklist]
        
        t_list = json.loads(trading_list['t_list{}'.format(c_rank)]) # 구매 테이블에 있는 코인 만 불러오기
        
        comnQueryWrk(curs, conn,"UPDATE trading_list SET t_list_chk{}={} WHERE coin_key= 1".format(c_rank,True))
        
        b_flag = False # 구매 제한 확인하기
        b_flag = limit_flag['b_limit']
        
        simulate = limit_flag['simulate']
        total_am = round(comnQuerySel(curs, conn,"SELECT or_am from deposit_holding WHERE coin_key=1")[0]['or_am'] * 0.88)
        
        for i in t_list['list']:
            idx = i
            try:
                if coin_list[i] not in blacklist_codes:
                    t_coin = comnQuerySel(curs, conn,"SELECT * FROM coin_list WHERE c_code='{}'".format(coin_list[i]))[0] # DB에서 코인이름을 기준으로 직접 값을 불러오는 파트
                else:
                    continue
            except Exception as e: 
                print(e)
                print('\ncoin data not found\n')
                t_coin = None
            # try: orderbook = tm.get_orderbook(t_coin['c_code'])[0] # 코인별 장표를 불러오는 프로세스
            # except: orderbook = {}
            chk1, chk2 = 0, 0
            try:
                if t_coin['record'] != 'NULL' and t_coin['record'] != None: 
                    t_coin['record'] = json.loads(t_coin['record'])
                    chk1, chk2 = t_coin['record']['case1_chk'], t_coin['record']['case2_chk']
            except Exception as e:
                logging.error("Unknown error 발생!")
                logging.error("Coin Code: {}".format(coin_list[i]))
                logging.error(traceback.format_exc())
            
            trade_factors, sma200, close_base = tm.get_all_factors(coin_list[i], 15)
            
            if t_coin != None and 'macd' in trade_factors.columns:    
                #RSI 지수 업데이트 {'c_code':item, 'position': "holding", 'rsi': None, 'record':c_ticker}
                t_coin['rsi'] = round(trade_factors.iloc[-1]['rsi'], 2)
                t_coin['record'] = {
                        'strategy': 'MACD rank: {}'.format(c_rank),
                        'close': trade_factors.iloc[-1]['close'],
                        'macd': round(trade_factors.iloc[-1]['macd'], 7),
                        'MACD_Signal': round(trade_factors.iloc[-1]['signal'], 7),
                        'rsi_K': round(trade_factors.iloc[-1]['rsi_K'], 2),
                        'rsi_D': round(trade_factors.iloc[-1]['rsi_D'], 2),
                        'case1_chk': chk1,
                        'case2_chk': chk2,                        
                    }
                
                if t_coin['hold'] == False: 
                    try: buying_process(c_rank=c_rank,sma200=sma200,trade_factors=trade_factors,t_record=t_coin, total_am=total_am, curs=curs,conn=conn)
                    except Exception as e:
                        logging.error("Exception 발생!")
                        logging.error(traceback.format_exc())
                        mp.post_message("#auto-trade", "{}: {}".format(t_coin['c_code'], e))
                        comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_coin['c_code'], 'ERROR',"""{}""".format(json.dumps(traceback.format_exc())),'', now))
                # 구매 절차 들어감
                sql_coin = t_coin
                sql_coin['record'] = json.dumps(t_coin['record']) # 거래기록을 DB에 저장
                comnQueryWrk(curs, conn,sqlText=sqlTextBuilder(li=sql_coin, table='coin_list'))
                if t_coin['hold'] == True and comnQuerySel(curs, conn,"SELECT COUNT(*) FROM coin_holding WHERE c_code='{}'".format(coin_list[i]))[0]['COUNT(*)'] == 0:
                    holding = {'c_code':sql_coin['c_code'], 'r_holding': False, 'c_rank': c_rank,  'simul_chk': simulate, 'position':sql_coin['position'], 
                                    'current_price': trade_factors.iloc[-1]['close'], 'current_percent': sql_coin['percent'], 'hold':sql_coin['hold'], 
                            'price_b':sql_coin['price_b'], 'rsi':sql_coin['rsi'], 'deposit':sql_coin['deposit'], 'user_call':user_call}
                    comnQueryWrk(curs, conn,sqlText=sqlTextBuilder(li=holding, table='coin_holding'))
                if t_coin['hold'] == True and comnQuerySel(curs, conn,"SELECT COUNT(*) FROM coin_list_selling WHERE c_code='{}'".format(coin_list[i]))[0]['COUNT(*)'] == 0: 
                    sell_coin = sql_coin
                    try: sell_coin.pop('buy_uuid')
                    except: pass
                    sell_coin['sell_uuid'] = ''
                    comnQueryWrk(curs, conn,sqlText=sqlTextBuilder(li=sell_coin, table='coin_list_selling'))    
                    del sell_coin
            del t_coin

            comnQueryWrk(curs, conn,"UPDATE trading_list SET t_list_chk{}={} WHERE coin_key= 1".format(c_rank,False))
            t.sleep(0.01)
    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt Exception 발생!")
        logging.error(traceback.format_exc())
        
        # 루프 안으로 exception check를 넣어서 문제가 5회 이상 발생시 긴급 판매 조치후 종료

    except Exception as e:
        logging.error("Exception 발생!")
        logging.error(traceback.format_exc())
        mp.post_message("#auto-trade", "{}: {}".format(coin_list[idx], e))
        comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}')".format("trading_log", coin_list[idx],'ERROR', '', """{}""".format(json.dumps(traceback.format_exc())), now))
    finally:
        comnQueryCls(curs, conn)


def is_v_shape_forming(data, window=7):
    # V자 형태가 생성되고 있는지 확인
    if (data['macd'].shift(window).iloc[-1] > data['macd'].iloc[-1]) and \
       (data['macd'].iloc[-1] == data['macd'].rolling(window=window).min().iloc[-1]) and \
       (data['macd'].rolling(window=window).apply(lambda x: x.is_monotonic_increasing).iloc[-1] == True):
        return True
    return False

def case1_check(trade_factors): # MACD 크로스 하락세 확인
    if trade_factors.iloc[-1]['signal'] < 0:
        if ((trade_factors.iloc[-1]['macd'] * 0.85) < trade_factors.iloc[-1]['signal']):
            return True
    elif trade_factors.iloc[-1]['signal'] > 0:
        if ((trade_factors.iloc[-1]['macd'] * 1.15) < trade_factors.iloc[-1]['signal']):
            return True
    return False

def macd_check(trade_factors):
    if trade_factors.iloc[-1]['signal'] < 0: 
        if (trade_factors.iloc[-1]['signal'] * 1.005) < trade_factors.iloc[-1]['macd'] < (trade_factors.iloc[-1]['signal'] * 0.995):
            return True
    elif trade_factors.iloc[-1]['signal'] > 0: # 극단적인 과매도 후 복구 되는지 확인하는 모듈
        if ((trade_factors.iloc[-1]['signal'] * 0.995) < trade_factors.iloc[-1]['macd'] < (trade_factors.iloc[-1]['signal'] * 1.005)):
            return True                    
    return False

def case2_check(trade_factors): # MACD 크로스 상승세 확인
    if trade_factors.iloc[-1]['signal'] < 0:
        if ((trade_factors.iloc[-1]['signal'] * 0.9999) < trade_factors.iloc[-1]['macd'] < (trade_factors.iloc[-1]['signal'] * 0.95)
            ) and (trade_factors.iloc[-2]['macd'] < trade_factors.iloc[-1]['macd']):
            return True
    elif trade_factors.iloc[-1]['signal'] > 0:
        if ((trade_factors.iloc[-1]['signal'] * 1.0001) < trade_factors.iloc[-1]['macd'] < (trade_factors.iloc[-1]['signal'] * 1.05)
            ) and (trade_factors.iloc[-2]['macd'] < trade_factors.iloc[-1]['macd']):
            return True
    return False

def sma_check(trade_factors):
    ema20 = trade_factors.iloc[-1]['sma20']
    ema50 = trade_factors.iloc[-1]['sma50']
    ema100 = trade_factors.iloc[-1]['sma100']
    ema200 = trade_factors.iloc[-1]['sma200']
    if ((ema200 * 1.0005) < ema100 
        ) and ((ema100 * 1.0005) < ema50
        ) and ((ema50 * 1.0005) < ema20 
        ):
        return True
    return False

def buying_process(trade_factors, sma200, c_rank, t_record, total_am:float, curs, conn):
    dt = datetime.datetime.now()
    mes = ''
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    global b_flag
    ubmi_data = comnQuerySel(curs, conn,"SELECT change_ubmi_now, change_ubmi_before FROM trading_list WHERE coin_key=1")[0]
    ubmi, ubmi_before = ubmi_data['change_ubmi_now'], ubmi_data['change_ubmi_before']
    # ubmi_digit = comnQuerySel(curs, conn,"SELECT ubmi FROM trading_list WHERE coin_key=1")[0]['ubmi']
    # orderbook으로 구매 판매 조절 
    # Ask = 매도 호가 (판매 예약이 걸려있는 금액) 
    # Bid = 매수 호가 (구매 예약이 걸려있는 금액)
    # 포지션이 buying 일 경우 오더 채크로 해당 주문이 완료 되었는지 확인한다. 
    # ubmi 지수 낮아지면 구매제한
    
    # 여기부터 구매 알고리즘 수정 시작
    cp = float(up.price_call(t_record['c_code'])[0]['tradePrice'])
    info = None
    am_invest = round(total_am/11)
    deposit = round((am_invest) - (am_invest * 0.0005))
    # 초기화
    case1_chk = case2_chk = False

    case1_chk = case1_check(trade_factors=trade_factors)
    case2_chk = case2_check(trade_factors=trade_factors)

    if case1_chk and t_record['record']['case1_chk'] == 0:
        t_record['record']['case1_chk'] = cp
    if case2_chk and t_record['record']['case2_chk'] == 0:
        t_record['record']['case2_chk'] = cp
        
    if t_record['record']['case1_chk'] > 0 and cp < t_record['record']['case1_chk'] and macd_check(trade_factors=trade_factors) == False: t_record['record']['case1_chk'] = cp
    
    if case2_chk and cp <= t_record['record']['case2_chk']: t_record['record']['case2_chk'] = cp
    
    if ((cp > (t_record['record']['case2_chk'] * 1.002)
        ) or (t_record['record']['case2_chk'] > 0 and trade_factors.iloc[-1]['signal'] > trade_factors.iloc[-1]['macd'])
        ) and case2_check(trade_factors=trade_factors) == False: 
        t_record['record']['case2_chk'] = 0
    if ((cp > (t_record['record']['case1_chk'] * 1.005)
        ) or (t_record['record']['case1_chk'] > 0 and trade_factors.iloc[-1]['signal'] < trade_factors.iloc[-1]['macd'])
        ) and case1_check(trade_factors=trade_factors) == False: 
        t_record['record']['case1_chk'] = 0
    
    condition1 = t_record['record']['case1_chk'] > 0 and t_record['hold'] == False and (
        trade_factors.iloc[-1]['rsi_K'] > trade_factors.iloc[-1]['rsi_D'] > 44) and (
        trade_factors.iloc[-2]['macd'] < trade_factors.iloc[-1]['macd']) and (
        trade_factors.iloc[-2]['macd'] <= trade_factors.iloc[-3]['macd'])
    
    condition2 = t_record['record']['case2_chk'] > 0 and t_record['hold'] == False and t_record['record']['case2_chk'] < cp and (
        trade_factors.iloc[-1]['rsi_K'] > trade_factors.iloc[-1]['rsi_D'] > 55) and (
        trade_factors.iloc[-2]['macd'] < trade_factors.iloc[-1]['macd']) and (
        trade_factors.iloc[-2]['macd'] >= trade_factors.iloc[-3]['macd'])
    
    condition3 = t_record['position'] in checking[1:]

    if(condition1 or condition2 or condition3) and b_flag == False:
        try:
            t_record['record']['case2_chk'] = 0
            t_record['record']['case1_chk'] = 0
            if b_flag == False and ((comnQuerySel(curs, conn,"SELECT COUNT(*) FROM coin_list_selling")[0]['COUNT(*)'] < 8) and (
                comnQuerySel(curs, conn,"SELECT dp_am FROM deposit_holding WHERE coin_key=1")[0]['dp_am'] >= ((total_am/11)*3))):
                mes = ''
                info = {}
                if simulate == False: # 시뮬레이션이 아닐때 
                    real_money, real_money_dp, real_money_sv = tm.real_trade_check()
                    if (real_money / 11) > 5000:
                        am_invest = round(real_money_dp / 11)
                        deposit = round((am_invest) - (am_invest * 0.0005))
                        if case1_chk == True: # 하락세 감지시
                            info = tm.limit_call_buy(coin=t_record['c_code'], price=cp, amt=deposit)
                            mes = '\n호가 급매수 진행 중'
                        elif case2_chk == True: # 상승세 감지시 
                            info = tm.trade_call_buy(coin=t_record['c_code'], amt=deposit)
                            mes = '\n호가 급매수 진행 중'
                        t_record['position'] = 'holding'
                        t_record['r_holding'] = True
                    else: # 금액 체크후 1회 구매 금액이 5000원 미만일 경우 UPBIT 결제가 안되기 때문에 변경
                        comnQueryWrk("UPDATE trade_rules SET simulate=1 WHERE coin_key=1")
                        info['uuid'] = "simulation"
                        info['volume'] = 0
                        t_record['position'] = 'holding'    
                else: 
                    info['uuid'] = "simulation"
                    info['volume'] = 0
                    t_record['position'] = 'holding'
                try: t_record['price_b'] = float(info['trades'][0]['price'])
                except: t_record['price_b'] = cp
                t_record['buy_uuid'] = info['uuid']
                try: cp = float(info['trades'][0]['price'])
                except: pass
                t_record['volume'] = info['volume']
                t_record['buy_uuid'] = info['uuid']
                comnQueryWrk(curs, conn,"UPDATE coin_list SET volume={}, buy_uuid='{}' WHERE c_code='{}'".format(info['volume'], info['uuid'], t_record['c_code']))  
            else: info = None
        
        except Exception as e:
            logging.error("Exception 발생!")
            logging.error(traceback.format_exc())
            mp.post_message("#auto-trade", "{}: {}, {}".format(t_record['c_code'], e, info))
            comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_record['c_code'],'ERROR', '', """{}""".format(json.dumps(traceback.format_exc())),dt))
            info = None
        
        if (info != None) and t_record['position'] not in checking and t_record['buy_uuid'] != '' and (
            comnQuerySel(curs, conn,"SELECT COUNT(*) FROM coin_list_selling WHERE c_code='{}'".format(t_record['c_code']))[0]['COUNT(*)'] == 0):
            # 구매 완료 메세지 보내는 파트
            # 이제 구매 완료시 체크하는 파트를 분리하여 일단 시뮬레이션이던 실거래이든 체크하는 파트에서 체크중 실거래시 구매 완료 메시지도 그쪽에서 처리. 
            if t_record['price_b'] == 0 or t_record['price_b'] == None: # 만약 price_b가 없을 경우 대비
                t_record['price_b'] = cp

            t_record['hold'] = True # 구매 완료후 설정 변경 
            t_record['deposit'] = deposit
            
            if condition1 == True: t_record['record']['strategy'] = 'case 1 B ' + t_record['record']['strategy']
            elif condition2 == True: t_record['record']['strategy'] = 'case 2 B ' + t_record['record']['strategy']
            report = "c_code: " + t_record['c_code'] +"\nprocess: BUY" + "\nc_rank: "+str(c_rank)+"\ncurrent price: "+str(cp)+"\ndate_time: " + str(dt_str) +"\nRSI: "+ str(t_record['rsi']) + "\nDeposit: W {}".format(t_record['deposit']) + "\nPurchased: {}".format(t_record['record']['strategy'])
            mp.post_message("#auto-trade", report) #Slack에 메세지 전송
            lst={'c_code': t_record['c_code'], 'c_rank': c_rank, 'current_price': cp, 'percent': -0.05, 'date_time':dt, 
                 'c_status': 'Purchased', 'reason': mes, 'deposit':t_record['deposit']}
            comnQueryWrk(curs, conn,sqlTextBuilder(li=lst,table='trade_history'))
            if simulate == False:
                comnQueryWrk(curs, conn,"UPDATE deposit_holding SET dp_am = dp_am - {} WHERE coin_key=2".format(am_invest)) # 전체 금액의 4%만 배분, total_am은 전체 88%
            else:
                comnQueryWrk(curs, conn,"UPDATE deposit_holding SET dp_am = dp_am - {} WHERE coin_key=1".format(am_invest))
            comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", t_record['c_code'],'BUY', json.dumps(t_record['record']), report,dt))
