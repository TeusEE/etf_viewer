# etf_viewer
한국에 상장된 ETF를 관찰하기 편하게 만들은 간단한 프로젝트입니다.

# 최초실행
```cmd
python -m pip install --upgrade pip setuptools
python -m pip install -r req.txt
python src/get_etf_list.py
python src/parsing_etf_list.py
python src/exec_from_etflist.py
streamlit run app.py
```

# 이후 실행 시
```cmd
streamlit run app.py
```