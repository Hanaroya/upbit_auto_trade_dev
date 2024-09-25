import requests
from bs4 import BeautifulSoup

user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'} 
def call_coin_list(): 
    krw_markets = []
    list_by_total = []

    url = "https://crix-api.upbit.com/v1/crix/trends/change_rate" 
    response = requests.get(url=url, headers=user_agent).json()
    markets = response

    for market in markets:
        if 'KRW-' in market['code']:
            krw_markets.append(market['code'].replace("CRIX.UPBIT.",''))
            market.update({'code':market['code'].replace("CRIX.UPBIT.",'')})
            list_by_total.append(market)

    return krw_markets, list_by_total

def call_by_total(): # 총 거래량 높은 순으로 정렬
    url = "https://www.coingecko.com/ko/거래소/upbit"
    bs = BeautifulSoup(requests.get(url).text,'html.parser')
    interest = []
    ticker_temp = bs.find_all("a", attrs={"rel":"nofollow noopener", "class":"mr-1"})
    print(ticker_temp)
    
    for i in range(50):
        interest.append('KRW-' + list(ticker_temp[i])[0][1:-5])
        
    return interest
