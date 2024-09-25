데이터 구조

coin_pl : 각 코인별 데이터 저장하는 manager 리스트 
구조: 
    { 
        'name': 코인 이름, 
        'position':"buying", (buying, holding, selling) 3가지 존재
        'rsi': None, 구매 체크용 rsi 지수 체크 
        'pr_rsi': None, rsi 지수 만들기용 지난 rsi 지수 기록한 리스트
        'record':[c_ticker] 각 코인별 호출 데이터 
    }