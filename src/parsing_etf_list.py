import csv
import aiofiles
import asyncio
# csv 파일을 읽어서 리스트로 가져오기


import httpx
async def fetch_and_save(tk_num):
    url = f"https://finance.naver.com/item/coinfo.naver?code={tk_num}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        async with aiofiles.open(f"./database/{tk_num}.html", "w+", encoding='utf-8') as fd:
            await fd.write(resp.text)


async def main():   
    import os
    import shutil
    try:
        shutil.rmtree("./database")
    except Exception as e:
        print(e)
    finally:
        os.mkdir("./database")
        
    with open('./etf_list.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader) 

    con_cnt = 10
    for idx in range(len(data)//con_cnt):        
        print(idx)
        await asyncio.gather(*[
            fetch_and_save(i[0])
            for i
            in data[idx*con_cnt:(idx+1)*con_cnt]
        ])
    await asyncio.gather(*[
        fetch_and_save(i[0])
        for i
        in data[(idx+1)*con_cnt:]
    ])

if __name__ == "__main__":    
    asyncio.run(main())