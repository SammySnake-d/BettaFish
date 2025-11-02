@echo off
REM 快速启动脚本 (Windows)

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python app.py
) else (
    python app.py
)
