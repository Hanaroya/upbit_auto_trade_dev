from comn import comnQueryStrt, comnQueryWrk, comnQueryCls
import main_multiprocessing_module as mmp

def initialize():
    conn, curs = comnQueryStrt()
    mmp.every_30_minutes()
    comnQueryWrk(curs, conn, "UPDATE trade_rules SET 30min_update_chk=1 WHERE coin_key=1")
    comnQueryCls(curs=curs, conn=conn)

if __name__ == "__main__":
    initialize()