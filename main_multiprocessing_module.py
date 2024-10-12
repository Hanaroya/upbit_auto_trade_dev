import datetime
import json
import logging
from multiprocessing import Process, Manager
import signal
import sys
from tabulate import tabulate
import pandas as pd
import time
import traceback
import os
import call_list_module as cl
import upbit_call_module as ub
import process_module_buying as bm
import process_module_selling as sm
import message_module as mm
import get_properties as gp
import trade_module as tm
from comn import comnQueryStrt, sqlTextBuilder, comnQueryWrk, comnQuerySel, comnQueryCls

manager = None # 프로세스 공유용 리스트 만드는 메니저
coin_pl = None # 프로세스간 공유 하는 코인 리스트
coin_b = None # trade history 거래 기록 저장용
list_by_total = [] #코인 리스트
sub_lists = [] # 거래량 별 코인 서브 리스트
process_list = [] # 멀티 프로섹스 리스트

#코인 리스트 큐로 만들기 {'name':'KRW-BTC', 'buy':False, 'record':[]} 레코드에 각 코인별 리스트 저장후 시작할때 리스트 번호로 분배,
#코인 리스트 리셋시 새롭게 번호 분배하는식으로 리스트 데이터 일관성 유지
#업비트 주문 요청 제외하면 초당 30회 요청 가능
def every_30_minutes(): # 30분마다 call해야하는 모듈 전부 여기에서 call
    # 30분 마다  코인 리스트를 최대 거래량 순으로 정렬해서 buying_module에 분배 
    conn, curs = comnQueryStrt()
    
    krw_markets, list_by_total = cl.call_coin_list()
    c_pl = []
    c_list = [d.get('c_code') for d in comnQuerySel(curs, conn, "SELECT c_code FROM coin_list")] # 전체 데이터 관리를 DB 통해서만 가능하게 수정 2023-05-18: 오후 04:48
    c_idx = 0
    trading_list = comnQuerySel(curs, conn, "SELECT * FROM trading_list WHERE coin_key= 1")[0]
    coin_pl = trading_list['coin_pl']
    
    for item in krw_markets: #코인 이름마다 현재 거래량 불러옴
        try: c_idx = c_list.index(item) # DB에 값이 저장되어 있으면 DB값 사용
        except: c_idx = -1
        if c_idx == -1: # DB에 없으면 초기값 부여
            pl ={
                    'c_code':item, 'position': "holding", 'hold': False, "buy_uuid": "", "volume": None, "r_holding": False,
                    'price_b': None, 'percent': 0, 'rsi': None, 'record': None, 'deposit': 0
                }
            sql_t = sqlTextBuilder(pl,'coin_list')
            comnQueryWrk(curs, conn, sql_t)
            c_list = [d.get('c_code') for d in comnQuerySel(curs, conn, "SELECT c_code FROM coin_list")] #만약 추가된 값이 있을경우 리스트 재구축
            c_pl.append(c_list[c_list.index(item)]) # krw_market 순서로 배치
        else: c_pl.append(c_list[c_idx])

    for item in c_pl:
        try: c_idx = krw_markets.index(item) # 만약 업비트 리스트에서 빠진 코인이 있을시 제거
        except: c_idx = -1
        if c_idx < 0: 
            comnQueryWrk(curs, conn, "DELETE FROM coin_list WHERE c_code='{}'".format(coin_pl.index(item)))
            t_pl = coin_pl
            t_pl.pop(coin_pl.index(item))
            coin_pl = t_pl
    
    list_sorted = sorted(list_by_total, key = lambda x: (x['accTradePrice24h']), reverse=True) #코인 거래총량으로 정렬
    if len(list_sorted) > 60: list_sorted = list_sorted[:60] # 상위 60개만 골라냄
    sub_lists = [list_sorted[i:i+12] for i in range(0, len(list_sorted), 12)] #코인 거래총량으로 정렬후 12개씩 나눔
    lt = 1
    for i in range(len(sub_lists)): # deadlock 방지용 체크 코드
        if trading_list['t_list_chk{}'.format(i+1)] == False: 
            time.sleep(0.1) # running 이 false일 경우 루프 탈출
            trading_list = comnQuerySel(curs, conn, "SELECT * FROM trading_list WHERE coin_key= 1")[0]
        t_list = {"list": [krw_markets.index(k['code']) for k in sub_lists[i]]}
        comnQueryWrk(curs, conn, "UPDATE trading_list SET t_list{}='{}', t_list_chk{}={} WHERE coin_key= 1".format(lt,json.dumps(t_list),lt,False))
        lt += 1
    coin_pl = c_pl # 총 거래량에 맞게 순서 변경
    comnQueryWrk(curs, conn, "UPDATE trading_list SET coin_pl='{}' WHERE coin_key= 1".format(json.dumps(coin_pl)))
    comnQueryCls(curs, conn)
    #UBMI 지수 호출후 재 분배

def every_1_hour(): # 1시간 마다 call해야하는 모듈 전부 여기에서 call 
    # 1시간 마다 수익 퍼센트, 수익금, 보험금액에서 얼마 줄었는지 표시
    conn, curs = comnQueryStrt()
    dp_earn = comnQuerySel(curs, conn, "SELECT pr_am FROM deposit_holding WHERE coin_key=1")[0]['pr_am']
    coin_holding = comnQuerySel(curs, conn, "SELECT c_code, current_price, price_b, current_percent, round(deposit+deposit*(current_percent/100)) AS deposit FROM coin_holding ORDER BY current_percent DESC")
    or_am = comnQuerySel(curs, conn, "SELECT or_am from deposit_holding WHERE coin_key=1")[0]['or_am']
    sv_am = comnQuerySel(curs, conn, "SELECT sv_am from deposit_holding WHERE coin_key=1")[0]['sv_am']
    remain = (round(or_am * 0.88) % 11) 
    sv_or = round(or_am * 0.12) + remain
    total_profit = 0
    if dp_earn != None: total_profit = dp_earn / or_am * 100
    
    tp = "---------------------------------\nHOURLY profit\nTotal Investment: W {}\nPercentage: {}%\nProfit: W {}\nSaving Amount: W {}\nSaving loss: W {}\n---------------------------------".format(or_am, format(total_profit, ".3f"),dp_earn, sv_or, sv_am) # 메세지 전달
    dt = pd.DataFrame(coin_holding)
    if len(dt) == 0:
        dt = ""
    now = datetime.datetime.now()
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "HOURLY_REPORT",'REPORT', "", '---------------------------------',now))
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "HOURLY_REPORT",'REPORT', '', tp, now))
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "HOURLY_REPORT",'REPORT', "", '---------------------------------',now))
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "HOURLY_REPORT",'REPORT', "", '---------------------------------',now))
    try:comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "HOURLY_REPORT",'REPORT', '', str(tabulate(dt, headers=dt.columns, floatfmt=".2f"),now)))
    except:comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "HOURLY_REPORT",'REPORT', "", '',now))
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "HOURLY_REPORT",'REPORT', "", '---------------------------------',now))
    mm.post_message("#auto-trade", tp)
    try: mm.post_message("#auto-trade", tabulate(dt, headers=dt.columns, floatfmt=".2f"))
    except: mm.post_message("#auto-trade", tabulate(dt, headers="", floatfmt=".2f"))
    comnQueryCls(curs, conn)

def server_ask_close():
    # 플라스크 서버에서 백엔드 종료 요청시
    conn, curs = comnQueryStrt()
    comnQueryWrk(curs, conn, "UPDATE trade_rules SET b_limit={} WHERE coin_key=1".format(True)) # 구매 제한으로 전 항목 판매 대기
    if comnQuerySel(curs, conn, "SELECT COUNT(*) FROM coin_holding")[0]['COUNT(*)'] > 0: return
 
    or_am = comnQuerySel(curs, conn, "SELECT or_am from deposit_holding WHERE coin_key=1")[0]['or_am']
    dp_am = round(or_am * 0.88)
    remain = (dp_am % 11) 
    dp_am = dp_am - remain
    sv_am = round(or_am * 0.12) + remain
    pr_am = comnQuerySel(curs, conn, "SELECT pr_am from deposit_holding WHERE coin_key=1")[0]['pr_am']
    sqls = ['TRUNCATE coin_holding', 'TRUNCATE trade_history', 'TRUNCATE coin_list',
            'UPDATE deposit_holding SET dp_am={}, sv_am={}, or_am={},pr_am={} WHERE coin_key=1;'.format(dp_am,sv_am,or_am,pr_am)]
    for sql in sqls: comnQueryWrk(curs, conn, sql)
    c_sql = comnQuerySel(curs, conn, "SELECT * FROM coin_list")
    for cs in c_sql:
        pl = {'c_code': cs['c_code'], 'position': "", 'hold': False,
                'price_b': None, 'percent': 0, 'rsi': None, 'record': cs['record'], 'deposit': 0}
        comnQueryWrk(curs, conn, sqlText=sqlTextBuilder(li=pl,table='coin_list'))
        time.sleep(0.1)
    comnQueryWrk(curs, conn, "UPDATE trade_rules SET terminate={}, b_limit={}, running=0, 30min_update_chk=0 WHERE coin_key=1".format(False,False))
    comnQueryCls(curs, conn)
    
def start_message():
    now = datetime.datetime.now()
    conn, curs = comnQueryStrt()
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report, dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "Trading_Begin",'START', "", '---------------------------------',now))
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report, dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "Trading_Begin",'START', "", 'auto-trade start',now))
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report, dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "Trading_Begin",'START', "", '---------------------------------',now))
    mm.post_message("#auto-trade", "---------------------------------")
    mm.post_message("#auto-trade", "auto-trade start")
    mm.post_message("#auto-trade", "---------------------------------")
    comnQueryCls(curs, conn)
    
def daily_report():
    myprops = gp.get_properties()
    now = datetime.datetime.now()
    conn, curs = comnQueryStrt()
    comnQueryWrk(curs, conn, "PURGE BINARY LOGS BEFORE '{}';".format(now)) # 매일 밤 11시 59분, SQL Server 로그 삭제, 이익금 반영
    mm.post_message("#auto-trade", "19:59pm: purge mysql server logs")
    comnQueryWrk(curs, conn, "UPDATE trade_rules SET b_limit={} WHERE coin_key=1".format(True)) # 수익 업데이트 완료까지 구매 제한
    simulate = comnQuerySel(curs, conn, "SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']

    or_am = comnQuerySel(curs, conn, "SELECT or_am from deposit_holding WHERE coin_key=1")[0]['or_am']
    pr_am = comnQuerySel(curs, conn, "SELECT pr_am from deposit_holding WHERE coin_key=1")[0]['pr_am']
    sv_pr = comnQuerySel(curs, conn, "SELECT sv_am from deposit_holding WHERE coin_key=1")[0]['sv_am']
    re_pr = round(or_am * 0.88) % 11
    or_new = or_am + pr_am
    
    dp_am = round(or_new * 0.88)
    remain = (dp_am % 11) 
    dp_am = dp_am - remain
    sv_am = round(or_new * 0.12) + remain
    sql = 'UPDATE deposit_holding SET dp_am={}, sv_am={}, or_am={},pr_am={} WHERE coin_key=1;'.format(dp_am,sv_am,or_new,0)
    comnQueryWrk(curs, conn, sql)
    sql = "INSERT INTO trade_result_history(date_time, total_investment, sv_am, income) VALUES ('{}',{},{},{})".format(now, or_am, sv_pr, pr_am)
    comnQueryWrk(curs, conn, sql)
    mm.post_message("#auto-trade", "Income added")
    comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "Income Added",'', "", '오늘자 정산 완료',now))
    
    coin_b = {'b_list':comnQuerySel(curs, conn, "SELECT * FROM trade_history")}
    coin_log = {'log_today': comnQuerySel(curs, conn, "SELECT * FROM trading_log")}
    date_time = datetime.datetime.now()
    dt = date_time.strftime('%Y-%m-%d %H.%M.%S %d')
    if len(list(coin_b['b_list'])) > 1:
        file_n = 'trade_result_'+str(dt)+'.xlsx'                
        mail_content = '''Today's trade result
        '''
        df = pd.DataFrame(data=list(coin_b['b_list']), 
                        columns=['c_code', 'current_price', 'percent', 'deposit', 'date_time', 'c_status', 'reason'])
        #convert into excel
        df.to_excel(file_n, index=False)
        mm.send_mail(myprops['GMAIL'], myprops['GMAIL'], 'Auto trade result '+str(dt), mail_content, [file_n], 
                    'smtp.gmail.com', 587, myprops['GMAIL_SENDER'], myprops['GMAIL_API'])
        os.remove(file_n)
        mm.post_message("#auto-trade", "{}: trade result sent to email".format(dt))
        comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "EMAIL",'', "", '투자 결과 이메일 발송',date_time))
    else: 
        mm.post_message("#auto-trade", "{}: no trade happens".format(dt))
        comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "NO EMAIL",'', "", '투자 결과 없음',date_time))
    if len(list(coin_log['log_today'])) > 1:
        date_time = datetime.datetime.now()
        dt = date_time.strftime('%Y-%m-%d %H.%M.%S %d')
        dir1 = os.getcwd()
        file_n = dir1+ "\\" + "log" + "\\" + 'trading_log_{}.xlsx'.format(str(dt)) # fix me: 파일 이름, 열리는 위치 확인 필요

        df = pd.DataFrame(data=list(coin_log['log_today']), 
                            columns=['c_code', 'position', 'record', 'report','dt_log'])
        #convert into excel
        df.to_excel(file_n, index=False)
        mm.post_message("#auto-trade", "{}: trade log saved".format(dt))
        comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "LOG_SAVED",'', "", '로그 저장 완료',date_time))
    else: 
        mm.post_message("#auto-trade", "{}: no trade happens".format(dt))
        comnQueryWrk(curs, conn, "INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", "NO_LOG_SAVED",'', "", '투자 결과 없음',date_time))
    
    comnQueryWrk(curs, conn, 'TRUNCATE trade_history')
    comnQueryWrk(curs, conn, 'TRUNCATE trading_log')
    comnQueryWrk(curs, conn, "UPDATE trade_rules SET b_limit={}, daily_report_chk={} WHERE coin_key=1".format(False, True)) # 수익 업데이트 완료까지 구매 제한
    del coin_b
    comnQueryCls(curs, conn)

def five_min_ubmi_update():
    conn, curs = comnQueryStrt()
    change_ubmi_before = comnQuerySel(curs, conn, "SELECT change_ubmi_now FROM trading_list WHERE coin_key=1")[0]['change_ubmi_now']
    total_ubmi, change_ubmi_now, fear_greed = ub.ubmi_call()
    if total_ubmi != None and change_ubmi_now != None and fear_greed != None:
        comnQueryWrk(curs, conn, "UPDATE trading_list SET total_ubmi={} WHERE coin_key= 1".format(total_ubmi))
        comnQueryWrk(curs, conn, "UPDATE trading_list SET change_ubmi_now={} WHERE coin_key= 1".format(change_ubmi_now))
        comnQueryWrk(curs, conn, "UPDATE trading_list SET change_ubmi_before={} WHERE coin_key= 1".format(change_ubmi_before))
        comnQueryWrk(curs, conn, "UPDATE trading_list SET fear_greed={} WHERE coin_key= 1".format(fear_greed))
    comnQueryCls(curs, conn)
# if __name__ == '__main__':
def main_backend_process():
    
    conn, curs = comnQueryStrt()
    
    coin_count = comnQuerySel(curs, conn, "SELECT COUNT(*) FROM coin_list")[0]['COUNT(*)']
    # myprops = gp.get_properties()
    try:
        # now = datetime.datetime.now()
        sh_list = []
        sub_lists = []
        if coin_count == 0:
            krw_markets, list_by_total = cl.call_coin_list() # 여기에 리스트 확인하는 체크 모듈 필요
            coin_pl = [] # 프로세스간 공유 하는 코인 리스트
    
            c_list = [d.get('c_code') for d in comnQuerySel(curs, conn, "SELECT c_code FROM coin_list")] # 전체 데이터 관리를 DB 통해서만 가능하게 수정 2023-05-18: 오후 04:48
            c_idx = 0
            
            for item in krw_markets: #코인 이름마다 현재 거래량 불러옴
                try: c_idx = c_list.index(item) # DB에 값이 저장되어 있으면 DB값 사용
                except: c_idx = -1
                if c_idx == -1: # DB에 없으면 초기값 부여
                    pl ={
                            'c_code':item, 'position': "holding", 'buy_uuid': '', 'volume': 0, 
                            'hold': False, 'price_b': None, 'percent': 0, 'rsi': None, 'record': None, 'deposit': 0
                        }
                    sql_t = sqlTextBuilder(pl,'coin_list')
                    comnQueryWrk(curs, conn, sql_t)
                    c_list = [d.get('c_code') for d in comnQuerySel(curs, conn, "SELECT c_code FROM coin_list")] #만약 추가된 값이 있을경우 리스트 재구축
                    coin_pl.append(c_list[c_list.index(item)])
                else: coin_pl.append(c_list[c_idx])
                # position: buying, selling, holding
                # buying: 사는 중 일때
                # selling: 파는 중 일때
                # holding: 구매, 판매중일때 
                # hold: True 코인 보유중, False 코인 없음
                # price_b: 코인 구입가
            for item in coin_pl:
                try: c_idx = krw_markets.index(item) # 만약 업비트 리스트에서 빠진 코인이 있을시 제거
                except: c_idx = -1
                if c_idx < 0: 
                    comnQueryWrk(curs, conn, "DELETE FROM coin_list WHERE c_code='{}'".format(coin_pl.index(item)))
                    t_pl = coin_pl
                    t_pl.pop(coin_pl.index(item))
                    coin_pl = t_pl
                
            list_sorted = sorted(list_by_total, key = lambda x: (x['accTradeVolume24h']), reverse=True) #코인 거래총량으로 정렬
            if len(list_sorted) > 60: list_sorted = list_sorted[:60] # 상위 60개만 골라냄
            sub_lists = [list_sorted[i:i+12] for i in range(0, len(list_sorted), 12)] #코인 거래총량으로 정렬후 12개씩 나눔
            lt = 1
            for item in sub_lists:
                t_l = {"list": [krw_markets.index(i['code']) for i in item]}
                sh_list.append(t_l)
                comnQueryWrk(curs, conn, "UPDATE trading_list SET t_list{}='{}', t_list_chk{}={} WHERE coin_key= 1".format(lt,json.dumps(t_l),lt,False))
                lt += 1
                #프로세스 도중 변경돼는 코인 리스트 갱신을 위해 추가함
            comnQueryWrk(curs, conn, "UPDATE trading_list SET coin_pl='{}' WHERE coin_key= 1".format(json.dumps(coin_pl)))
        else:
            for i in range(5):
                sh_list.append(json.loads(comnQuerySel(curs, conn, "SELECT t_list{} FROM trading_list WHERE coin_key=1".format(i+1))[0]['t_list{}'.format(i+1)]))
                
        for task in sh_list:
            process_list.append(Process(target=bm.coin_receive_buying, args=[sh_list.index(task) + 1], daemon=True)) 
            #각 프로세스별 코인 갱신기능 추가
        # process_list.append(Process(target=sm.coin_receive_selling, args=[], daemon=True)) # 판매용 프로세스
        
        for p in process_list:
            p.start()
        
        del sh_list, coin_pl
    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt Exception 발생!")
        logging.error(traceback.format_exc())
    except Exception:
        logging.error("Exception 발생!")
        logging.error(traceback.format_exc())
    finally: 
        comnQueryCls(curs, conn)

def initialize_database():
    conn, curs = comnQueryStrt()
    try:
        # 고정된 금액 설정
        dp_am = 880000
        sv_am = 120000
        or_am = 1000000
        pr_am = 0

        # 테이블 초기화 및 업데이트
        sqls = [
            'TRUNCATE coin_holding',
            'TRUNCATE trade_history',
            'TRUNCATE coin_list',
            'UPDATE deposit_holding SET dp_am={}, sv_am={}, or_am={}, pr_am={} WHERE coin_key=1'.format(dp_am, sv_am, or_am, pr_am),
            'UPDATE trade_rules SET b_limit=True, terminate=False, running=0, 30min_update_chk=0 WHERE coin_key=1'
        ]
        
        for sql in sqls:
            comnQueryWrk(curs, conn, sql)

        # coin_list 테이블 재구성
        c_sql = comnQuerySel(curs, conn, "SELECT * FROM coin_list")
        for cs in c_sql:
            pl = {
                'c_code': cs['c_code'],
                'position': "",
                'hold': False,
                'price_b': None,
                'percent': 0,
                'rsi': None,
                'record': cs['record'],
                'deposit': 0
            }
            comnQueryWrk(curs, conn, sqlText=sqlTextBuilder(li=pl, table='coin_list'))
            time.sleep(0.01)  # 서버 부하 방지를 위한 짧은 대기

        print("데이터베이스 초기화가 완료되었습니다.")
    except Exception as e:
        print(f"데이터베이스 초기화 중 오류 발생: {str(e)}")
    finally:
        comnQueryCls(curs, conn)

# 함수 사용 예시
if __name__ == "__main__":
    initialize_database()