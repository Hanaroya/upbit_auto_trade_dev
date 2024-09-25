import datetime
import pymysql
import get_properties as gp

myprops = gp.get_properties()

def comnQueryStrt():
    conn = pymysql.connect(
        host=myprops['host'],
        port=int(myprops['port']),
        user=myprops['user'], 
        password=myprops['password'], 
        database=myprops['database']
    )
    curs = conn.cursor(pymysql.cursors.DictCursor)
    return conn, curs

def chkNone(typ):
    if typ == None:
        return 'NULL'
    elif type(typ) == datetime.datetime: 
        return "'{}'".format(typ)
    else: return typ

def sqlTextBuilder(li:dict, table:str):
    sql_t = ''
    if table == 'coin_holding':
        sql_t = """INSERT INTO {}(c_code, r_holding, c_rank, simul_chk, position, current_price, current_percent, hold, price_b, rsi, deposit, user_call)
        VALUES ('{}',{},{},{},'{}',{},{},{},{},{},{},{}) ON DUPLICATE KEY UPDATE c_code='{}', r_holding={},c_rank={},simul_chk={},position='{}',current_price={},current_percent={},hold={}, 
        price_b={}, rsi={}, deposit={}, user_call={}
        """.format(table, 
                   chkNone(li['c_code']),chkNone(li['r_holding']),chkNone(li['c_rank']),chkNone(li['simul_chk']),chkNone(li['position']),chkNone(li['current_price']),chkNone(li['current_percent']),
                   chkNone(li['hold']),chkNone(li['price_b']),
                   chkNone(li['rsi']),chkNone(li['deposit']),chkNone(li['user_call']),
                   chkNone(li['c_code']),chkNone(li['r_holding']),chkNone(li['c_rank']),chkNone(li['simul_chk']),chkNone(li['position']),chkNone(li['current_price']),chkNone(li['current_percent']),
                   chkNone(li['hold']),chkNone(li['price_b']),
                   chkNone(li['rsi']),chkNone(li['deposit']),chkNone(li['user_call']))
    elif table == 'coin_list': 
        sql_t = """INSERT INTO {}(c_code, r_holding, position, buy_uuid, volume, hold, price_b, rsi, record, deposit, percent)
        VALUES ('{}',{},'{}','{}',{},{},{},{},'{}',{},{}) ON DUPLICATE KEY UPDATE c_code='{}',r_holding={}, position='{}',buy_uuid='{}',volume={},hold={}, 
        price_b={}, rsi={}, record='{}', deposit={}, percent={}""".format(table, 
                   chkNone(li['c_code']),chkNone(li['r_holding']),chkNone(li['position']),chkNone(li['buy_uuid']),chkNone(li['volume']),
                   chkNone(li['hold']),chkNone(li['price_b']),chkNone(li['rsi']),
                   chkNone(li['record']),chkNone(li['deposit']),chkNone(li['percent']),
                   chkNone(li['c_code']),chkNone(li['r_holding']),chkNone(li['position']),chkNone(li['buy_uuid']),chkNone(li['volume']),
                   chkNone(li['hold']),chkNone(li['price_b']),chkNone(li['rsi']),
                   chkNone(li['record']),chkNone(li['deposit']),chkNone(li['percent']))
    elif table == 'coin_list_selling': 
        sql_t = """INSERT INTO {}(c_code, r_holding, position, sell_uuid, volume, hold, price_b, rsi, record, deposit, percent)
        VALUES ('{}',{},'{}','{}',{},{},{},{},'{}',{},{}) ON DUPLICATE KEY UPDATE c_code='{}', r_holding={}, position='{}',sell_uuid='{}',volume={},hold={}, 
        price_b={}, rsi={}, record='{}', deposit={}, percent={}""".format(table, 
                   chkNone(li['c_code']),chkNone(li['r_holding']),chkNone(li['position']),chkNone(li['sell_uuid']),chkNone(li['volume']),
                   chkNone(li['hold']),chkNone(li['price_b']),chkNone(li['rsi']),
                   chkNone(li['record']),chkNone(li['deposit']),chkNone(li['percent']),
                   chkNone(li['c_code']),chkNone(li['r_holding']),chkNone(li['position']),chkNone(li['sell_uuid']),chkNone(li['volume']),
                   chkNone(li['hold']),chkNone(li['price_b']),chkNone(li['rsi']),
                   chkNone(li['record']),chkNone(li['deposit']),chkNone(li['percent']))
    elif table == 'trade_history': 
        sql_t = "INSERT INTO {}(c_code, c_rank, current_price, percent, date_time, c_status, reason, deposit) VALUES ('{}',{},{},{},{},'{}','{}',{});".format(table, 
        chkNone(li['c_code']),chkNone(li['c_rank']),chkNone(li['current_price']),chkNone(li['percent']),
        chkNone(li['date_time']),chkNone(li['c_status']),chkNone(li['reason']),chkNone(li['deposit']))
    elif table == 'trade_rules': 
        return 0
    return sql_t

def comnQueryWrk(curs, conn, sqlText):
    sql = sqlText
    curs.execute(sql)
    conn.commit()

def comnQuerySel(curs, conn, sqlText):
    sql = sqlText
    curs.execute(sql)
    conn.commit()
    sqlVal = curs.fetchall()
    return sqlVal

def comnQueryCls(curs, conn):
    curs.close()
    conn.close()