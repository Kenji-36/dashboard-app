@echo off
chcp 65001 > nul
echo ダッシュボードを起動しています...
echo.
venv\Scripts\python.exe -m streamlit run app.py
pause

