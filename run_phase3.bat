@echo off
chcp 65001
echo ========================================
echo Phase 3 ダッシュボード起動中...
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo エラー: 仮想環境が見つかりません。
    pause
    exit /b 1
)

echo 仮想環境を使用してダッシュボードを起動します...
echo.

venv\Scripts\python.exe -m streamlit run src\app.py

pause

