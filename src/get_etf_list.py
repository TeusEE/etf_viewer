import FinanceDataReader as fdr
df = fdr.StockListing('ETF/KR')
etf_info = [
    [row["Symbol"], row["Name"]]
    for idx, row in 
    df.loc[:, ["Symbol", "Name"]].iterrows()
]


import csv
with open('./etf_list.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(etf_info)
