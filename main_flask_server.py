import atexit
import json
from flask import Flask, jsonify, make_response, redirect, render_template, request
from flask_bootstrap import Bootstrap
from flask_apscheduler import APScheduler
from apscheduler.executors.debug import DebugExecutor
import datetime
import pymysql
from flask import Flask, render_template, request, jsonify
import message_module as mp
import trade_module as tm
import get_properties as gp
import main_multiprocessing_module as mmp
from comn import comnQueryStrt, sqlTextBuilder, comnQueryWrk, comnQuerySel, comnQueryCls
from werkzeug.security import generate_password_hash, check_password_hash
import process_module_buying as mb
import process_module_selling as ms
import time as t

# 기본 설정 세팅
myprops = gp.get_properties()
st = False
ss = False
lb = False
ls = False
message1 = "초기 상태 입니다."
message2 = "초기 상태 입니다."
message3 = "초기 상태 입니다."
message4 = "초기 상태 입니다."
# 기본 메시지 + 중요 아이디, 비밀번호 불러오는 파트

#플라스크 선언 + 스캐쥴러 + 부트스트렙 선언
class Config:
    SCHEDULER_API_ENABLED = True
    
app = Flask(__name__, static_url_path='')
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
Bootstrap(app)
#플라스크 선언 + 스캐쥴러 + 부트스트렙 선언


# Mocked user data with encrypted passwords
users = [ # 로그인 데이터
    {'id': 1, 'username': myprops['site_user'], 'password': generate_password_hash(myprops['password'])},
]

ubmi_data = {
    'value1': 0,
    'value2': 0,
    'value3': 0
}

@app.route('/')
def home():
    conn, curs = comnQueryStrt()
    global cookie, myprops, message1, st,ss,lb,ls
    st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
    ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']
    lb = comnQuerySel(curs, conn,"SELECT b_limit FROM trade_rules WHERE coin_key=1")[0]['b_limit']
    ls = comnQuerySel(curs, conn,"SELECT s_limit FROM trade_rules WHERE coin_key=1")[0]['s_limit']
    comnQueryCls(curs, conn)
    if request.cookies.get('logged_in') and check_password_hash(request.cookies.get('logged_in'), myprops['site_user']+myprops['password']):
        if message1 == "자동거래가 종료되었습니다.": message1 = "초기 상태 입니다."
        return render_template('home.html', test1=st, test2=ss, test3=lb, test4=ls, 
                               message1=message1, message2=message2, message3=message3, message4=message4)
    else:
        return redirect('/login')

@app.route('/coin_graph')
def coin_graph():
    coin_code = request.args.get('coin_code')

    conn, curs = comnQueryStrt()
    try: 
        coin = comnQuerySel(curs, conn,"SELECT c_code FROM coin_holding WHERE c_code = '{}'".format(coin_code))
        if coin[0] is None:
            return jsonify({"error": "Coin not found"}), 404

        trade_factors, sma200, close_base = tm.get_all_factors(coin=coin[0]['c_code'], min=15)
        # Example data for graphs (replace with actual data)
        data = {
            'main_data': trade_factors[['date', 'open', 'high', 'low', 'close', 'volume']].to_dict(orient='records'),
            'rsi_data': trade_factors[['date', 'rsi']].to_dict(orient='records'),
            'stoch_rsi_data': trade_factors[['date', 'rsi_K', 'rsi_D']].to_dict(orient='records'),
            'macd_data': trade_factors[['date', 'macd', 'signal']].to_dict(orient='records')
        }
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        comnQueryCls(curs, conn)

    return jsonify(data)

def update_values():
    conn, curs = comnQueryStrt()
    ubmi_data['value1'] = comnQuerySel(curs, conn,"SELECT total_ubmi FROM trading_list WHERE coin_key=1")[0]['total_ubmi']
    ubmi_data['value2'] = comnQuerySel(curs, conn,"SELECT change_ubmi_now FROM trading_list WHERE coin_key=1")[0]['change_ubmi_now']
    ubmi_data['value3'] = comnQuerySel(curs, conn,"SELECT fear_greed FROM trading_list WHERE coin_key=1")[0]['fear_greed']
    comnQueryCls(curs, conn)

def buying_process(rank):
    # if 구매 제한 체크, 작동중 체크, 
    conn, curs = comnQueryStrt()
    t_list_chk = "t_list_chk{}".format(rank)
    try:
        coin_count = comnQuerySel(curs, conn, "SELECT COUNT(*) FROM coin_list")[0]['COUNT(*)']
        wait_30 = comnQuerySel(curs, conn,"SELECT 30min_update_chk FROM trade_rules WHERE coin_key=1")[0]['30min_update_chk']
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        # lb = comnQuerySel(curs, conn,"SELECT b_limit FROM trade_rules WHERE coin_key=1")[0]['b_limit']
        run_chk = comnQuerySel(curs, conn,"SELECT {} FROM trading_list WHERE coin_key=1".format(t_list_chk))[0]['{}'.format(t_list_chk)]
        if st == True and tt == False and wait_30 == True and coin_count > 60 and run_chk == False:
            mb.coin_receive_buying(c_rank=rank)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        comnQueryWrk(curs, conn,"UPDATE trading_list SET t_list_chk{}={} WHERE coin_key=1".format(rank,False))
        comnQueryCls(curs, conn)

def selling_process_regular():
    # if 판매 제한 체크, 작동중 체크, 
    conn, curs = comnQueryStrt()
    sell_list_chk = "sell_list_chk"
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ls = comnQuerySel(curs, conn,"SELECT s_limit FROM trade_rules WHERE coin_key=1")[0]['s_limit']
        run_chk = comnQuerySel(curs, conn,"SELECT {} FROM trading_list WHERE coin_key=1".format(sell_list_chk))[0]['{}'.format(sell_list_chk)]
        if st == True and ls == False and tt == False and run_chk == False:
            comnQueryWrk(curs, conn,"UPDATE trading_list SET sell_list_chk={} WHERE coin_key=1".format(True))
            ms.coin_receive_regular_selling()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        comnQueryWrk(curs, conn,"UPDATE trading_list SET sell_list_chk={} WHERE coin_key=1".format(False))
        comnQueryCls(curs, conn) 

def selling_process_user():
    # if 판매 제한 체크, 작동중 체크, 
    conn, curs = comnQueryStrt()
    sell_list_chk = "sell_list_chk"
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ls = comnQuerySel(curs, conn,"SELECT s_limit FROM trade_rules WHERE coin_key=1")[0]['s_limit']
        run_chk = comnQuerySel(curs, conn,"SELECT {} FROM trading_list WHERE coin_key=1".format(sell_list_chk))[0]['{}'.format(sell_list_chk)]
        if st == True and ls == False and tt == False and run_chk == False:
            comnQueryWrk(curs, conn,"UPDATE trading_list SET sell_list_chk={} WHERE coin_key=1".format(True))
            ms.coin_receive_user_selling()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        comnQueryWrk(curs, conn,"UPDATE trading_list SET sell_list_chk={} WHERE coin_key=1".format(False))
        comnQueryCls(curs, conn) 

def terminate_process():
    conn, curs = comnQueryStrt()
    try:
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        if tt == True:
            mmp.daily_report()
            mmp.server_ask_close()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    comnQueryCls(curs, conn)
    

###################################################################################################
# APScheduler 설정 각 스캐쥴 마다 terminate 확인 체크 필요
###################################################################################################

import threading
from apscheduler.schedulers.background import BackgroundScheduler

# 각 함수에 대한 잠금 객체 생성
buying_process_lock1 = threading.Lock()
buying_process_lock2 = threading.Lock()
buying_process_lock3 = threading.Lock()
buying_process_lock4 = threading.Lock()
buying_process_lock5 = threading.Lock()
selling_process_lock1 = threading.Lock()
selling_process_lock2 = threading.Lock()
buy_check_lock = threading.Lock()
sell_check_lock = threading.Lock()

@scheduler.task('cron', id='clean_blacklist', coalesce=False, max_instances=1, second='*/15')
def clean_blacklist():
    conn, curs = comnQueryStrt()
    try:
        timeout = comnQuerySel(conn=conn, curs=curs, sqlText="SELECT c_code FROM blacklist")
        for coin in timeout:
            query = """
            UPDATE blacklist SET
                    timeout = CASE 
                                WHEN TIMESTAMPDIFF(MINUTE, date, NOW()) >= timeout THEN 0
                                ELSE timeout
                            END
            WHERE c_code ='{}'
            """.format(coin['c_code'])
            comnQueryWrk(curs=curs, conn=conn, sqlText=query)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    
@scheduler.task('cron', id='truncate_blacklist', coalesce=False, max_instances=1, hour='8')
def truncate_blacklist():
    conn, curs = comnQueryStrt()
    try:
        query = """
        TRUNCATE TABLE blacklist
        """
        comnQueryWrk(curs=curs, conn=conn, sqlText=query)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    
@scheduler.task('cron', id='hourly_report', coalesce=False, max_instances=1, minute=0, second=0)
def hourly_report(): # 1시간 간격 리포트 전송 
    # if 작동중 체크, 
    conn, curs = comnQueryStrt()
    try: 
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        if st == True and tt == False:
            mmp.every_1_hour()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

@scheduler.task('cron', id='hourly_coin_list_check', coalesce=False, max_instances=1, minute='*/30', second=0)
def hourly_coin_list_check():  # 30분 간격 코인 리스트 다시 정렬 (거래 대금순)
    # if 작동중 체크, 
    conn, curs = comnQueryStrt()
    try: 
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        if st == True and tt == False:
            mmp.every_30_minutes()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

@scheduler.task('cron', id='five_min_ubmi_update', coalesce=False, max_instances=1, minute='*/5')
def five_min_ubmi_update(): #  UBMI 지수 (코인 거래량) 체크용 5분 간격
    # if 작동중 체크, 
    mmp.five_min_ubmi_update()


@scheduler.task('cron', id='daily_report', coalesce=False, max_instances=1,  hour='19-21', second='*/20')
def daily_report():
    # if 작동중 체크, 
    conn, curs = comnQueryStrt()
    try: 
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        dt = comnQuerySel(curs, conn,"SELECT daily_report_chk FROM trade_rules WHERE coin_key=1")[0]['daily_report_chk']
        coin_num = comnQuerySel(curs, conn, "SELECT COUNT(*) FROM coin_list_selling")[0]['COUNT(*)']
        if st == True and tt == False and dt == False and coin_num == 0:
            mmp.daily_report()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

@scheduler.task('cron', id='daily_report_chk', coalesce=False, max_instances=1, hour='5-18', minute='*/20')
def daily_report_chk():
    conn, curs = comnQueryStrt()
    try: 
        dt = comnQuerySel(curs, conn,"SELECT daily_report_chk FROM trade_rules WHERE coin_key=1")[0]['daily_report_chk']
        if dt == True:
            comnQueryWrk(curs, conn, "UPDATE trade_rules SET daily_report_chk={} WHERE coin_key=1".format(False))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)   

@scheduler.task('cron', id='ubmi_check', coalesce=False, max_instances=1, minute='*/5')
def ubmi_check():
    conn, curs = comnQueryStrt()
    try: 
        ubmi_data = comnQuerySel(curs, conn,"SELECT change_ubmi_now, change_ubmi_before FROM trading_list WHERE coin_key=1")[0]
        ubmi, ubmi_before = ubmi_data['change_ubmi_now'], ubmi_data['change_ubmi_before']
        query = ""
        if ubmi - ubmi_before < -5: # 자꾸 시간대별로 안돌길래 변경
            query = "UPDATE trade_rules SET b_limit=1 WHERE coin_key=1"
        if ubmi - ubmi_before > 5:
            query = "UPDATE trade_rules SET b_limit=0 WHERE coin_key=1"
        if ubmi < -20:
            query = "UPDATE trade_rules SET b_limit=1 WHERE coin_key=1"
        if ubmi > 0:
            query = "UPDATE trade_rules SET b_limit=0 WHERE coin_key=1"
        comnQueryWrk(curs, conn, query)
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)   

@scheduler.task('cron', id='up_down_check', coalesce=False, max_instances=1, minute='*/5')
def up_down_check():
    conn, curs = comnQueryStrt()
    try: 
        coin_data = comnQuerySel(curs, conn,"SELECT * FROM coin_holding")
        for t_coin in coin_data:
            mp.regular_percent_message(channel="#auto-trade",coin=t_coin['c_code'], percent=t_coin['current_percent'])
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)   

# @scheduler.task('cron', id='regular_buying_hour1', coalesce=False, max_instances=1, hour='14-23', minute='*/5')
# def regular_buying_hour1():
#     conn, curs = comnQueryStrt()
#     try: 
#         dt = comnQuerySel(curs, conn,"SELECT b_limit FROM trade_rules WHERE coin_key=1")[0]['b_limit']
#         if dt == False:
#             comnQueryWrk(curs, conn, "UPDATE trade_rules SET b_limit={} WHERE coin_key=1".format(True))
#     except pymysql.MySQLError as e:
#         print(f"Error: {e}")
#     finally: comnQueryCls(curs, conn)   

# @scheduler.task('cron', id='regular_buying_hour2', coalesce=False, max_instances=1, hour='0-4', minute='*/5')
# def regular_buying_hour2():
#     conn, curs = comnQueryStrt()
#     try: 
#         dt = comnQuerySel(curs, conn,"SELECT b_limit FROM trade_rules WHERE coin_key=1")[0]['b_limit']
#         if dt == False:
#             comnQueryWrk(curs, conn, "UPDATE trade_rules SET b_limit={} WHERE coin_key=1".format(True))
#     except pymysql.MySQLError as e:
#         print(f"Error: {e}")
#     finally: comnQueryCls(curs, conn)   
    
@scheduler.task('cron', id='buy_check', coalesce=False, max_instances=1, second="*/10")
def buy_check():
    conn, curs = comnQueryStrt()
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']
        real_holdings = comnQuerySel(curs, conn,"SELECT c_code, r_holding, buy_uuid FROM coin_list_selling WHERE r_holding=1")
        run_chk = comnQuerySel(curs, conn,"SELECT buy_chk FROM trading_list WHERE coin_key=1")[0]['buy_chk']
        if st == True and tt == False and run_chk == False: 
            if ss == False: 
                comnQueryWrk(curs, conn,"UPDATE trading_list SET buy_chk={} WHERE coin_key=1".format(True))
                for coin in real_holdings: # 여기에 uuid가 포함되어 있는 코인을 호출해서 해당 구매 기록이 완전한지 확인
                    info = tm.orders_status(orderid=coin['buy_uuid']) # 구매 상황 체크
                    if info != None and info['state'] != 'wait' and info['side'] == 'bid' and coin['r_holding'] == False:
                        dt = datetime.datetime.now()
                        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        cp = info['trades']['price']
                        report = "c_code: " + coin['c_code'] +"\ncurrent price: "+str(cp)+"\ndate_time: "+ str(dt_str) + "\nDeposit: W {}".format( info['trades']['funds']) + "Real Trade"
                        mp.post_message("#auto-trade", report) #Slack에 메세지 전송
                        comnQueryWrk(curs, conn,"UPDATE coin_list_selling SET r_holding=1, volume={} WHERE c_code='{}'".format(info['volume'],coin['c_code']))
                        comnQueryWrk(curs, conn,"UPDATE coin_holding SET r_holding=1 WHERE c_code='{}'".format(coin['c_code']))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        comnQueryWrk(curs, conn,"UPDATE trading_list SET buy_chk={} WHERE coin_key=1".format(False))
        comnQueryCls(curs, conn)
        
@scheduler.task('cron', id='sell_check', coalesce=False, max_instances=1, second="*/10")
def sell_check():
    conn, curs = comnQueryStrt()
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']
        real_holdings = comnQuerySel(curs, conn,"SELECT * FROM coin_list_selling WHERE r_holding=1")
        run_chk = comnQuerySel(curs, conn,"SELECT sell_chk FROM trading_list WHERE coin_key=1")[0]['sell_chk']
        if st == True and tt == False and run_chk == False:
            if ss == False: 
                comnQueryWrk(curs, conn,"UPDATE trading_list SET sell_chk={} WHERE coin_key=1".format(True))
                for coin in real_holdings: # 여기에 uuid가 포함되어 있는 코인을 호출해서 해당 판매 기록이 완전한지 확인
                    info = tm.orders_status(orderid=coin['sell_uuid']) # 구매 상황 체크
                    if info != None and info['state'] != 'wait' and info['side'] == 'bid' and coin['r_holding'] == True: 
                        #이익금 정리
                        dt = datetime.datetime.now()
                        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        cp = info['trades']['price']
                        profit_earn = info['trades']['funds'] - info['paid_fee']
                        up_chk_b = -0.05 # 전체 수익의 25% ~ 50%일 경우 긴급판매 발동  
                        up_chk_b += ((float(cp) - coin['price_b']) / coin['price_b']) * 100
                        per_deal = format(up_chk_b, ".3f")
                        message = "c_code: " + coin['c_code'] +"\nprocess: SELL-REAL"+"\nprice_b: "+ str(coin['price_b'])+"\nprice_s: "+str(cp)+ "\ndate_time: " + str(dt_str) +"\nStrategy: "+ str(coin['record']['strategy']) + "\nresult: {}%, W {}".format(per_deal, profit_earn)+"\nSOLD: {}".format("USER Decision")
                        
                        mp.post_message("#auto-trade", message) #Slack에 메세지 전송
                        # 결과 DB 전송 
                        lst={'c_code': coin['c_code'], 'c_rank':int(coin['record']['strategy'][-1]), 'current_price': cp, 'percent': per_deal, 'date_time':dt, 'c_status': 'SOLD-REAL: {}'.format(coin['record']['strategy']), 'reason': "USER Decision", 'deposit': profit_earn}
                        comnQueryWrk(curs, conn,sqlTextBuilder(li=lst,table='trade_history')) #거래 기록 추가
                        
                        comnQueryWrk(curs, conn,"INSERT INTO {}(c_code, position, record, report,dt_log) VALUES ('{}','{}','{}','{}','{}')".format("trading_log", coin['c_code'],'SELL-REAL', json.dumps(coin['record']), message,dt))
                        
                        comnQueryWrk(curs, conn,"DELETE FROM coin_list_selling WHERE c_code='{}'".format(coin['c_code'])) #판매 리스트에서 제거
                        comnQueryWrk(curs, conn,"DELETE FROM coin_holding WHERE c_code='{}'".format(coin['c_code'])) #코인 보유 리스트에서 제거   
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        comnQueryWrk(curs, conn,"UPDATE trading_list SET sell_chk={} WHERE coin_key=1".format(False))
        comnQueryCls(curs, conn)

@scheduler.task('cron', id='get_real_balance', coalesce=False, max_instances=1, second="*/30")
def get_real_balance():
    conn, curs = comnQueryStrt()
    try: 
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']

        if st == True and tt == False:
            if ss == False: 
                tm.trade_strt()
                comnQueryWrk(curs, conn,"UPDATE deposit_holding SET or_am={} WHERE coin_key=2".format(tm.get_balance("KRW")))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

@scheduler.task('cron', id='buying_process_wrapper1', coalesce=False, max_instances=1, second='*/4', args=[1])        
def buying_process_wrapper1(*args): # 구매용 매소드 실행시키기
    if buying_process_lock1.acquire(blocking=False):
        try:
            buying_process(*args)
        finally:
            buying_process_lock1.release()
    else:
        print("이전 buying_process가 아직 실행 중입니다.")
    
@scheduler.task('cron', id='buying_process_wrapper2', coalesce=False, max_instances=1, second='*/6', args=[2])        
def buying_process_wrapper2(*args): # 구매용 매소드 실행시키기
    if buying_process_lock2.acquire(blocking=False):
        try:
            t.sleep(0.5)
            buying_process(*args)
        finally:
            buying_process_lock2.release()
    else:
        print("이전 buying_process가 아직 실행 중입니다.")
    
@scheduler.task('cron', id='buying_process_wrapper3', coalesce=False, max_instances=1, second='*/12', args=[3])        
def buying_process_wrapper3(*args): # 구매용 매소드 실행시키기
    if buying_process_lock3.acquire(blocking=False):
        try:
            t.sleep(1)
            buying_process(*args)
        finally:
            buying_process_lock3.release()
    else:
        print("이전 buying_process가 아직 실행 중입니다.")

@scheduler.task('cron', id='buying_process_wrapper4', coalesce=False, max_instances=1, second='*/20', args=[4])        
def buying_process_wrapper4(*args): # 구매용 매소드 실행시키기
    if buying_process_lock4.acquire(blocking=False):
        try:
            t.sleep(2)
            buying_process(*args)
        finally:
            buying_process_lock4.release()
    else:
        print("이전 buying_process가 아직 실행 중입니다.")

@scheduler.task('cron', id='buying_process_wrapper5', coalesce=False, max_instances=1, second='*/30', args=[5])        
def buying_process_wrapper5(*args): # 구매용 매소드 실행시키기
    if buying_process_lock5.acquire(blocking=False):
        try:
            t.sleep(5)
            buying_process(*args)
        finally:
            buying_process_lock5.release()
    else:
        print("이전 buying_process가 아직 실행 중입니다.")

@scheduler.task('cron', id='selling_process_wrapper1', coalesce=False, max_instances=1, minute='*/2')
def selling_process_wrapper1(): # 판매용 메소드 실행시키기 5분 간격
    if selling_process_lock1.acquire(blocking=False):
        try:
            selling_process_regular()
        finally:
            selling_process_lock1.release()
    else:
        print("이전 selling_process가 아직 실행 중입니다.")

@scheduler.task('cron', id='selling_process_wrapper2', coalesce=False, max_instances=1, second='*/5')
def selling_process_wrapper2(): # 판매용 메소드 실행시키기 5분 간격
    if selling_process_lock2.acquire(blocking=False):
        try:
            t.sleep(0.5)
            selling_process_user()
        finally:
            selling_process_lock2.release()
    else:
        print("이전 selling_process가 아직 실행 중입니다.")


@scheduler.task('cron', id='buy_check_wrapper', coalesce=False, max_instances=1, second='*/5')
def buy_check_wrapper(): # 실제 구매 기록이 있을시 5초마다 해당 uuid 조회
    if buy_check_lock.acquire(blocking=False):
        try:
            buy_check()
        finally:
            buy_check_lock.release()
    else:
        print("이전 buy_check가 아직 실행 중입니다.")

@scheduler.task('cron', id='sell_check_wrapper', coalesce=False, max_instances=1, second='*/5')
def sell_check_wrapper(): # 실제 판매 기록이 있을시 5초마다 해당 uuid 조회
    if sell_check_lock.acquire(blocking=False):
        try:
            sell_check()
        finally:
            sell_check_lock.release()
    else:
        print("이전 sell_check가 아직 실행 중입니다.")

############ 플라스크 종료를 위한 코드 ##############
# atexit.register(lambda: scheduler.shutdown())
atexit.register(lambda: mmp.server_ask_close())
############ 플라스크 종료를 위한 코드 ##############

@app.route('/ubmi')
def get_data():
    update_values()
    return jsonify(ubmi_data)

@app.route('/login')
def login():
    if request.cookies.get('logged_in') and check_password_hash(request.cookies.get('logged_in'), myprops['site_user']+myprops['password']):
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = next((user for user in users if user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            response = make_response(redirect('/'))
            response.set_cookie('logged_in', generate_password_hash(myprops['site_user']+myprops['password']))
            return response
        else: return redirect('/login')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    response = make_response(redirect('/login'))
    response.set_cookie('logged_in', 'false')
    return response

@app.route('/initialize_database', methods=['POST'])
def api_initialize_database():
    try:
        mmp.initialize_database()
        return jsonify({"message": "데이터베이스 초기화가 성공적으로 완료되었습니다."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/start_trading', methods=['POST'])
def start_trading():
    global st, message1, lb

    if request.method == 'POST':
        if 'start_trading' in request.form:
            st = not st
        if st == True: 
            mmp.start_message()
            start_backend()
            message1 = "자동거래가 시작되었습니다."
        else: 
            terminate_backend()
            lb = True
            message1 = "자동거래가 종료되었습니다."
    return redirect('/')

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    global ss, message2, message1

    if request.method == 'POST' and message1 != "초기 상태 입니다.":
        if 'start_simulation' in request.form:
            ss = not ss
        if ss == True: 
            start_simulation_backend() # 시뮬레이션은 현재 디폴트로 True
            message2 = "시뮬레이션이 시작되었습니다."
        else: 
            end_simulation_backend()
            message2 = "시뮬레이션이 종료되었습니다."
    return redirect('/')

@app.route('/limit_buying', methods=['POST'])
def limit_buying():
    global lb, message3, message1

    if request.method == 'POST':
        if 'limit_buying' in request.form and message1 != "초기 상태 입니다.":
            lb = not lb
            if st == False and message1 == "자동거래가 종료되었습니다.":
                lb == True
        if lb == True: 
            restrict_buying_backend()
            message3 = "구매 제한이 시작되었습니다."
        else: 
            no_restrict_buying_backend()
            message3 = "구매 제한이 종료되었습니다."
    return redirect('/')

@app.route('/limit_selling', methods=['POST'])
def limit_selling():
    global ls, message4, message1

    if request.method == 'POST' and message1 != "초기 상태 입니다.":
        if 'limit_selling' in request.form:
            ls = not ls
        if ls == True: 
            restrict_selling_backend()
            message4 = "판매 제한이 시작되었습니다."
        else: 
            no_restrict_selling_backend()
            message4 = "판매 제한이 종료되었습니다."
    return redirect('/')

@app.route('/coin_holdings')
def coin_holdings():
    if request.cookies.get('logged_in') and check_password_hash(request.cookies.get('logged_in'), myprops['site_user']+myprops['password']):
        # Connect to the database
        
        conn, curs = comnQueryStrt()
        # Retrieve data from the coin_holding table
        coin_data = comnQuerySel(curs, conn,"SELECT * FROM coin_holding ORDER BY current_percent DESC")
        comnQueryCls(curs, conn)
        # Render the HTML template with the coin data
        return render_template('coin_holdings.html', coin_data=coin_data)
    else:
        return redirect('/login')

@app.route('/trading_report')
def trading_report():
    if request.cookies.get('logged_in') and check_password_hash(request.cookies.get('logged_in'), myprops['site_user']+myprops['password']):
        # Connect to the MySQL database
        

        # Execute a query to fetch the required data
        conn, curs = comnQueryStrt()
        query = "SELECT or_am, pr_am, dp_am, sv_am, FORMAT(pr_am / or_am * 100,3) AS profit_percentage FROM deposit_holding WHERE coin_key=1"
        or_am = comnQuerySel(curs, conn,"SELECT or_am from deposit_holding WHERE coin_key=1")[0]['or_am']
        dp_am = comnQuerySel(curs, conn,"SELECT dp_am from deposit_holding WHERE coin_key=1")[0]['dp_am']
        re_pr = round(or_am * 0.88) % 11
        
        data = comnQuerySel(curs, conn,query)
        data[0]['sv_or'] = round(or_am * 0.12) + re_pr
        data[0]['dp_am'] = dp_am
        # Close the database connection
        comnQueryCls(curs, conn)
        
        return render_template('trading_report.html', data=data)
    else:
        return redirect('/login')

@app.route('/trading_history')
def trading_history():
    if request.cookies.get('logged_in') and check_password_hash(request.cookies.get('logged_in'), myprops['site_user']+myprops['password']):
        # Connect to the MySQL database
        
        conn, curs = comnQueryStrt()
        # Execute a query to fetch the required data
        query = "SELECT * FROM trade_result_history"
        data = comnQuerySel(curs, conn,query)
        # Close the database connection
        comnQueryCls(curs, conn)
        
        return render_template('trading_history.html', data=data)
    else:
        return redirect('/login')
    
@app.route('/simulation_sell', methods=['POST'])
def simulation_sell():
    coin_id = request.args.get('coin_id')
    conn, curs = comnQueryStrt()
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        
        r_check = comnQuerySel(curs, conn,"SELECT r_holding FROM coin_list_selling WHERE c_code='{}'".format(coin_id)) # 실제 코인 미 보유를 확인
        if r_check == True:
            return jsonify({"result": -1})
        if st == True and tt == False:
            comnQueryWrk(curs, conn,"UPDATE coin_holding SET user_call=1 WHERE c_code='{}'".format(coin_id))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    return redirect('/coin_holdings')

@app.route('/sell_urgent', methods=['POST'])
def sell_urgent():
    coin_id = request.form.get('coin_id')
    coin_volume = request.form.get('coin_volume')
    conn, curs = comnQueryStrt()
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']
        r_check = comnQuerySel(curs, conn,"SELECT r_holding FROM coin_list_selling WHERE c_code='{}'".format(coin_id)) # 실제 코인 미 보유를 확인
        if st == True and tt == False:
            if ss == False and r_check == True: 
                tm.trade_strt()
                info = tm.trade_call_sell(coin=coin_id, volume=coin_volume)
                comnQueryWrk(curs, conn,"UPDATE coin_list_selling SET sell_uuid='{}' WHERE c_code='{}'".format(info['uuid'],coin_id))
            else:
                return jsonify({"result": -1})
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    return redirect('/coin_holdings')

@app.route('/buy_urgent', methods=['POST'])
def buy_urgent():
    coin_id = request.form.get('coin_id')
    coin_amt = request.form.get('coin_amt')
    conn, curs = comnQueryStrt()
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']

        if st == True and tt == False:
            if ss == False: 
                tm.trade_strt()
                info = tm.trade_call_buy(coin=coin_id, amt=coin_amt)
                comnQueryWrk(curs, conn,"UPDATE coin_list_selling SET buy_uuid='{}' WHERE c_code='{}'".format(info['uuid'],coin_id))            
            else:
                return jsonify({"result": -1})
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    return redirect('/coin_holdings')

@app.route('/sell_limit', methods=['POST'])
def sell_limit():
    coin_id = request.form.get('coin_id')
    coin_price = request.form.get('coin_price')
    coin_volume = request.form.get('coin_volume')
    conn, curs = comnQueryStrt()
    try:
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']
        r_check = comnQuerySel(curs, conn,"SELECT r_holding FROM coin_list_selling WHERE c_code='{}'".format(coin_id)) # 실제 코인 보유를 확인
        if st == True and tt == False:
            if ss == False and r_check == True: 
                tm.trade_strt()
                info = tm.limit_call_sell(coin=coin_id, price=coin_price, volume=coin_volume)
                comnQueryWrk(curs, conn,"UPDATE coin_list_selling SET sell_uuid='{}' WHERE c_code='{}'".format(info['uuid'],coin_id))
            else:
                return jsonify({"result": -1})
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    return redirect('/coin_holdings')

@app.route('/buy_limit', methods=['POST'])
def buy_limit():
    coin_id = request.form.get('coin_id')
    coin_price = request.form.get('coin_price')
    coin_amt = request.form.get('coin_amt')
    conn, curs = comnQueryStrt()
    try: 
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']

        if st == True and tt == False:
            if ss == False: 
                tm.trade_strt()
                info = tm.limit_call_buy(coin=coin_id, price=coin_price, amt=coin_amt)
                comnQueryWrk(curs, conn,"UPDATE coin_list_selling SET buy_uuid='{}' WHERE c_code='{}'".format(info['uuid'],coin_id))
            else: 
                
                return jsonify({"result": -1})
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    return redirect('/coin_holdings')

@app.route('/get_real_volume', methods=['POST'])
def get_real_volume():
    coin_id = request.args.get('coin_id')
    conn, curs = comnQueryStrt()
    try: 
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']
        info = None
        
        if st == True and tt == False:
            if ss == False: 
                info = comnQuerySel(curs, conn,"SELECT volume FROM coin_list_selling WHERE c_code='{}'".format(coin_id))[0]['volume']
            else: info = 0
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:comnQueryCls(curs, conn)
    return jsonify({"volume": info})

@app.route('/get_real_balance', methods=['POST'])
def get_real_balance_api():
    conn, curs = comnQueryStrt()
    try: 
        st = comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running']
        tt = comnQuerySel(curs, conn,"SELECT terminate FROM trade_rules WHERE coin_key=1")[0]['terminate']
        ss = comnQuerySel(curs, conn,"SELECT simulate FROM trade_rules WHERE coin_key=1")[0]['simulate']
        info = None
        
        if st == True and tt == False:
            if ss == False: 
                info = comnQuerySel(curs, conn,"SELECT or_am FROM deposit_holding WHERE coin_key=2")[0]['or_am']
            else: info = 0
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    return jsonify({"volume": info})

@app.route('/cancel_buy_order', methods=['POST'])
def cancel_buy_order():
    data = request.json
    coin_id = data['coin_id']
    conn, curs = comnQueryStrt()
    success = False
    try:
        chk = comnQuerySel(conn=conn, curs=curs, sqlText="SELECT r_holding, buy_uuid FROM coin_list_selling WHERE c_code='{}'".format(coin_id))
        if chk[0]['r_holding'] == True and chk[0]['buy_uuid'] != '':
            tm.cancel_order_uuid(uuid=chk[0]['buy_uuid'])
            success = True
        # 데이터베이스에서 해당 코인의 구매 주문을 찾아 취소    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    
    if success:
        return jsonify({"result": 0})
    else:
        return jsonify({"result": -1})

@app.route('/cancel_sell_order', methods=['POST'])
def cancel_sell_order():
    data = request.json
    coin_id = data['coin_id']
    conn, curs = comnQueryStrt()
    success = False
    try:
        chk = comnQuerySel(conn=conn, curs=curs, sqlText="SELECT r_holding, sell_uuid FROM coin_list_selling WHERE c_code='{}'".format(coin_id))
        if chk[0]['r_holding'] == True and chk[0]['sell_uuid'] != '':
            tm.cancel_order_uuid(uuid=chk[0]['sell_uuid'])
            success = True
        # 데이터베이스에서 해당 코인의 구매 주문을 찾아 취소    
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
    
    if success:
        return jsonify({"result": 0})
    else:
        return jsonify({"result": -1})
    
def start_backend(): # 벡엔드 시작 커맨드
    conn, curs = comnQueryStrt()
    try: 
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == False: 
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET running={} WHERE coin_key=1".format(True)) 
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

def terminate_backend(): # 벡엔드 종료 커맨드: 보유 코인 판매 완료까지 대기 
    conn, curs = comnQueryStrt()
    try: 
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == True:
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET running={} WHERE coin_key=1".format(False))
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET terminate={} WHERE coin_key=1".format(True))
            terminate_process()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

def start_simulation_backend(): # 실거래 시뮬레이션으로 전환 커멘드
    conn, curs = comnQueryStrt()
    try: 
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == False:
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET simulate={} WHERE coin_key=1".format(True))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

def end_simulation_backend(): # 시뮬레이션 실거래 전환 커맨드
    conn, curs = comnQueryStrt()
    try: 
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == True:
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET simulate={} WHERE coin_key=1".format(False))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

def restrict_buying_backend(): # 구매 제한 커멘드
    conn, curs = comnQueryStrt()
    try: 
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == True:
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET b_limit={} WHERE coin_key=1".format(True))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)

def restrict_selling_backend(): # 판매 제한 커멘드
    conn, curs = comnQueryStrt()
    try:
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == True:
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET s_limit={} WHERE coin_key=1".format(True))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)        

def no_restrict_buying_backend(): # 구매 제한 해제 커멘드
    conn, curs = comnQueryStrt()
    try:
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == True:
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET b_limit={} WHERE coin_key=1".format(False))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)    

def no_restrict_selling_backend(): # 판매 제한 해제 커멘드
    conn, curs = comnQueryStrt()
    try:
        if comnQuerySel(curs, conn,"SELECT running FROM trade_rules WHERE coin_key=1")[0]['running'] == True:
            comnQueryWrk(curs, conn,"UPDATE trade_rules SET s_limit={} WHERE coin_key=1".format(False))
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally: comnQueryCls(curs, conn)
        


# if __name__ == '__main__':
#     conn, curs = comnQueryStrt()
#     mmp.every_30_minutes()
#     comnQueryWrk(curs, conn, "UPDATE trade_rules SET 30min_update_chk=1 WHERE coin_key=1")
#     comnQueryCls(curs=curs, conn=conn)
#     app.run(host="0.0.0.0", use_reloader=False)