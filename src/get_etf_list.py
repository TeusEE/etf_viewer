from pykrx import stock

# 한국거래소 전체 ETF 티커(코드)와 종목명 반환
etf_df = stock.get_etf_ticker_list()
# ticker와 name을 동시에 얻고 싶다면 get_market_ohlcv_by_ticker 사용
# 여기서는 ticker와 이름을 매핑한 DataFrame을 만듭니다.
etf_info = []
for ticker in etf_df:
    name = stock.get_etf_ticker_name(ticker)
    etf_info.append([ticker, name])

import csv
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(etf_info)