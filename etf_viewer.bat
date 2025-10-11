@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ===============================
REM 1️⃣ Python 가상환경 활성화
REM ===============================
echo [가상환경 활성화 중...]
call .venv\Scripts\activate.bat

if errorlevel 1 (
    echo ❌ 가상환경을 활성화하지 못했습니다. 경로를 확인하세요.
    pause
    exit /b
)
echo ✅ 가상환경이 활성화되었습니다.
echo.

REM ===============================
REM 2️⃣ 실행 기록 확인용 로그 파일
REM ===============================
set LOG_FILE=last_run.log

REM 현재 시간 (UNIX timestamp)
for /f %%a in ('powershell -command "[int][double]::Parse((Get-Date -UFormat %%s))"') do set NOW=%%a

REM 하루(24시간) = 86400초
set /a DAY=86400

echo ============================
echo [ETL 실행 체크 시작]
echo 현재 시간: %NOW%
echo ============================

REM 로그 파일이 존재하면 변수로 로드
if exist %LOG_FILE% (
    for /f "tokens=1,2 delims==" %%a in (%LOG_FILE%) do (
        set %%a=%%b
    )
) else (
    echo LOG_FILE이 없습니다. 새로 생성됩니다.
)

REM ===============================
REM 3️⃣ 스크립트 실행 (24시간 내 실행 시 SKIP)
REM ===============================
set SCRIPT1=src\get_etf_list.py
set KEY1=GET_ETF
call :maybe_run "%SCRIPT1%" "%KEY1%"

set SCRIPT2=src\parsing_etf_list.py
set KEY2=PARSING_ETF
call :maybe_run "%SCRIPT2%" "%KEY2%"

set SCRIPT3=src\exec_from_etflist.py
set KEY3=EXEC_ETF
call :maybe_run "%SCRIPT3%" "%KEY3%"

REM ===============================
REM 4️⃣ Streamlit 실행
REM ===============================
echo ============================
echo [Streamlit 실행 시작]
echo ============================
streamlit run app.py

goto :eof


:maybe_run
set SCRIPT=%~1
set KEY=%~2
set LAST_VAR=!%KEY%!
if defined LAST_VAR (
    set /a DIFF=%NOW% - !LAST_VAR!
    if !DIFF! LSS %DAY% (
        echo [SKIP] %SCRIPT% — 최근 24시간 내 실행됨.
        goto :eof
    )
)
echo [RUN] %SCRIPT%
python %SCRIPT%
if !errorlevel! == 0 (
    REM 실행 성공 시 현재 시간을 로그 파일에 갱신
    call :update_log %KEY% %NOW%
)
goto :eof


:update_log
set KEY=%~1
set VALUE=%~2
REM 기존 로그에서 같은 KEY 제거 후 새로 추가
findstr /v "^%KEY%=" %LOG_FILE% > temp.log 2>nul
echo %KEY%=%VALUE%>>temp.log
move /y temp.log %LOG_FILE% >nul
goto :eof
