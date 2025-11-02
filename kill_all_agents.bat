@echo off
setlocal enabledelayedexpansion
REM 一键杀死所有 Agent 进程的脚本 (Windows 版本)
REM 用于在更新代码前清理所有运行中的服务

echo =========================================
echo 开始停止所有 Agent 进程...
echo =========================================
echo.

set KILLED_COUNT=0

REM 定义所有使用的端口
set PORTS=5000 8501 8502 8503 8601 8602 8603

REM 遍历所有端口，查找并杀死对应进程
for %%P in (%PORTS%) do (
    echo.
    echo 检查端口 %%P...
    
    REM 查找占用该端口的进程
    for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P"') do (
        if not "%%A"=="" (
            echo   ⚠ 发现进程: PID=%%A
            echo   → 正在终止进程 %%A...
            taskkill /PID %%A /F >nul 2>&1
            if !errorlevel! equ 0 (
                echo   ✓ 进程 %%A 已成功终止
                set /a KILLED_COUNT+=1
            ) else (
                echo   ✗ 无法杀死进程 %%A
            )
        )
    )
)

echo.
echo =========================================
echo 检查残留的 Streamlit 和 Flask 进程...
echo =========================================

REM 查找所有 streamlit 进程
echo 查找 Streamlit 进程...
tasklist /FI "IMAGENAME eq python.exe" /V 2>nul | findstr /I "streamlit" >nul
if !errorlevel! equ 0 (
    echo 发现 Streamlit 相关进程，正在终止...
    for /f "tokens=2" %%A in ('tasklist /FI "IMAGENAME eq python.exe" /V 2^>nul ^| findstr /I "streamlit"') do (
        echo   → 终止进程 %%A
        taskkill /PID %%A /F >nul 2>&1
        if !errorlevel! equ 0 (
            set /a KILLED_COUNT+=1
        )
    )
) else (
    echo   ✓ 没有残留的 Streamlit 进程
)

REM 查找所有包含 app.py 的 Python 进程
echo 查找 Flask (app.py) 进程...
tasklist /FI "IMAGENAME eq python.exe" /V 2>nul | findstr /I "app.py" >nul
if !errorlevel! equ 0 (
    echo 发现 Flask 相关进程，正在终止...
    for /f "tokens=2" %%A in ('tasklist /FI "IMAGENAME eq python.exe" /V 2^>nul ^| findstr /I "app.py"') do (
        echo   → 终止进程 %%A
        taskkill /PID %%A /F >nul 2>&1
        if !errorlevel! equ 0 (
            set /a KILLED_COUNT+=1
        )
    )
) else (
    echo   ✓ 没有残留的 Flask 进程
)

echo.
echo =========================================
echo 清理完成！
echo 共终止 %KILLED_COUNT% 个进程
echo =========================================
echo.
echo 提示: 现在可以安全地更新代码并重新启动应用
echo.
pause
