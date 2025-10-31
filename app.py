import streamlit as st
import pandas as pd
import streamlit.components.v1 as components   # ← iframe 삽입용
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(
    page_title="My App",   # (선택) 페이지 제목
    layout="wide",         # <‑‑ wide 모드 지정
    initial_sidebar_state="auto",   # (선택) 사이드바 초기 상태
)

# ────────────────────── 데이터 로드 & 컬럼명 변경 ──────────────────────
df = pd.read_csv("etf_info.csv", encoding="utf-8-sig", index_col=0)
df["회사"] = df["etf명_한글"].apply(lambda x : x.split(" ")[0])
del df["etf세부정보"]
df = df.rename(columns={
    "1개월_수익률": "1M",
    "3개월_수익률": "3M",
    "6개월_수익률": "6M",
    "1년_수익률": "1Y"
})
#df["시가총액"] = pd.to_numeric(df["시가총액"].apply(lambda x : int(x/10_000)))
df["시가총액"] = (
    df["시가총액"]    
    .astype(float)                       # 한 번에 float 로 변환
    .floordiv(10_000)                    # 10,000 단위 정수화    
)

# ★ dtype 검증
assert pd.api.types.is_float_dtype(df["시가총액"]), "시가총액 컬럼이 정수형이 아닙니다!"
    
def get_price():
    import requests
    from bs4 import BeautifulSoup
    url = "https://finance.naver.com/marketindex/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    prices = soup.select(".head_info .value")
    return prices[0].text

def change_price(sess):    
    import datetime
    sess["usd_ratio"] = f"{get_price()}, {datetime.datetime.now()}시간 기준."

# ---- 선택된 종목코드 저장용 session_state 초기화 ----
if "selected_code" not in st.session_state:
    st.session_state["selected_code"] = None
    st.session_state["usd_ratio"] = get_price()

# ────────────────────── 레이아웃 (좌·우 2열) ──────────────────────
col_left, col_right = st.columns([3, 4])   # 비율을 바꾸고 싶다면 [2,1] 등으로 조정
etf_dividend_url = "https://www.k-etf.com/calendar/dividend"
# ─ 왼쪽: 테이블 ─
with col_left:    
    st.subheader("ETF 정보")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("etf명", hide=True)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    for col in df.columns:
        if col == "etf명_한글":
            gb.configure_column(col, autoSize=True, filter="agTextColumnFilter")
        elif col != "etf명":
            gb.configure_column(col, autoSize=True, maxWidth=120, minWidth=10)

    gb.configure_column(
        "시가총액",
        type=["numericColumn"],          # 숫자 컬럼 타입
        headerName="시가총액(억)",
        sortable=True,
        filter="agNumberColumnFilter",   # 숫자 전용 필터        
    )
    
    initial_sort = [
        {"colId": "회사",  "sort": "desc"},   # A col
        {"colId": "시가총액",       "sort": "desc"}   # B col
    ]

    gb.configure_grid_options(
        multiSort=True,          # ↗︎ 다중 정렬 허용
        sortModel=initial_sort,   # ↗︎ 초기 정렬 순서
        multiSortKey='ctrl'
    )
    
    # 행 더블클릭 이벤트 등록    
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.NO_UPDATE,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=False,
        height=400,        
    )

    # 선택된 데이터 처리
    selected_rows = grid_response["selected_rows"]
    if isinstance(selected_rows, list) and len(selected_rows) > 0:
        selected_code = selected_rows[0]["etf명"]
        st.session_state["selected_code"] = selected_code
    elif hasattr(selected_rows, "empty") and not selected_rows.empty:
        selected_code = selected_rows.iloc[0]["etf명"]
        st.session_state["selected_code"] = selected_code    
    st.write("현재 달러 환율 : {}".format(st.session_state["usd_ratio"]))
    if st.button("환율정보 갱신"):
        change_price(st.session_state)    
    st.image("https://ssl.pstatic.net/imgfinance/chart/marketindex/area/month3/FX_USDX.png", width='stretch')    
    st.image("https://ssl.pstatic.net/imgfinance/chart/marketindex/area/month3/FX_USDKRW.png", width='stretch')
    

# ─ 오른쪽: iframe ─
with col_right:    
    st.subheader("ETF 관련 사이트")    
    if st.session_state["selected_code"]:
        code = st.session_state["selected_code"]
        iframe_url = f"https://finance.naver.com/item/coinfo.naver?code={code}"
        html_code = f"""
        <iframe src="{iframe_url}" 
                style="width:100%; height:100vh; border:none;" 
                scrolling="yes"></iframe>
        """
        components.html(html_code, height=1000)
    else:
        st.info("왼쪽에서 ETF 종목을 선택하면 상세 정보가 여기에 표시됩니다.")
