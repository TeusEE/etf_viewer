from bs4 import BeautifulSoup
import aiofiles as aos

async def exec_file(filenm):
    async with aos.open(f"./database/{filenm}", "r+", encoding='utf-8') as fd:
        ret = BeautifulSoup(await fd.read(), "html.parser")
        m1_profit = ret.select_one("#tab_con1 > div:nth-child(6) > table > tbody > tr:nth-child(1) > td > em").get_text().strip()
        m3_profit = ret.select_one("#tab_con1 > div:nth-child(6) > table > tbody > tr:nth-child(2) > td > em").get_text().strip()
        m6_profit = ret.select_one("#tab_con1 > div:nth-child(6) > table > tbody > tr:nth-child(3) > td > em").get_text().strip()
        m12_profit = ret.select_one("#tab_con1 > div:nth-child(6) > table > tbody > tr:nth-child(4) > td > em").get_text().strip()
        fund_tax = ret.select_one("#tab_con1 > div:nth-child(4) > table > td > em").get_text().strip()   
        total_stock_cnt = ret.select_one("#tab_con1 > div.first > table > tr:nth-child(3) > td > em").get_text().strip()                    
        price = ret.select_one("#on_board_last_nav > em > strong").get_text().strip()        
        detail = ret.select_one("div.summary_info > p").get_text().strip()
        def str_proc(mystr):
            if mystr == "N/A":
                return None
            return float(mystr.replace("%", ""))
        return {
            "etf명" : filenm.split(".")[0],
            "1개월_수익률" : str_proc(m1_profit),
            "3개월_수익률" : str_proc(m3_profit),
            "6개월_수익률" : str_proc(m6_profit),
            "1년_수익률" : str_proc(m12_profit),
            "총보수" : str_proc(fund_tax),
            "시가총액" : int(total_stock_cnt.replace(",",""))*int(price.replace(",","")),
            "etf세부정보" : detail
        }
        
        

async def main():    
    import os
    tg_list = os.listdir("./database")    
    ret = await asyncio.gather(*[
        exec_file(i)
        for i in 
        tg_list
    ])

    import pandas as pd
    dt = pd.DataFrame(ret)    
    meta_dt = pd.read_csv("etf_list.csv", header = None, names = ["etf명", "etf명_한글"])
    fin_dt = meta_dt.merge(dt, how = "outer", left_on= "etf명", right_on="etf명")     

    fin_dt.to_csv("etf_info.csv")
    
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())