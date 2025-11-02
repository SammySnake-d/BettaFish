@echo off
REM 微舆 (BettaFish) 一键部署脚本 - Windows 版本

echo ==========================================
echo   微舆 (BettaFish) 一键部署脚本
echo ==========================================
echo.

REM 检查 Python
echo 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python。请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 找到 Python %PYTHON_VERSION%
echo √ Python 已安装
echo.

REM 询问是否创建虚拟环境
set /p CREATE_VENV="是否创建 Python 虚拟环境? (推荐) [Y/n]: "
if "%CREATE_VENV%"=="" set CREATE_VENV=Y

if /i "%CREATE_VENV%"=="Y" (
    echo 创建虚拟环境...
    if not exist venv (
        python -m venv venv
        echo √ 虚拟环境创建成功
    ) else (
        echo √ 虚拟环境已存在
    )
    
    REM 激活虚拟环境
    call venv\Scripts\activate.bat
    echo √ 虚拟环境已激活
) else (
    echo 跳过虚拟环境创建
)

echo.

REM 升级 pip
echo 升级 pip...
python -m pip install --upgrade pip -q
echo √ pip 已升级
echo.

REM 安装依赖
echo 安装 Python 依赖包...
echo 这可能需要几分钟时间，请耐心等待...
if exist requirements.txt (
    python -m pip install -r requirements.txt -q
    echo √ Python 依赖包安装完成
) else (
    echo 错误: requirements.txt 文件不存在
    pause
    exit /b 1
)

echo.

REM 安装 Playwright 浏览器
echo 安装 Playwright 浏览器...
python -m playwright install chromium
echo √ Playwright 浏览器安装完成
echo.

REM 可选：安装 WebDAV 支持
set /p INSTALL_WEBDAV="是否安装 WebDAV 云备份支持? [Y/n]: "
if "%INSTALL_WEBDAV%"=="" set INSTALL_WEBDAV=Y

if /i "%INSTALL_WEBDAV%"=="Y" (
    echo 安装 WebDAV 支持...
    python -m pip install webdavclient3 -q
    echo √ WebDAV 支持已安装
)

echo.

REM 创建必要的目录
echo 创建必要的目录...
if not exist logs mkdir logs
if not exist reports mkdir reports
if not exist final_reports mkdir final_reports
if not exist insight_engine_streamlit_reports mkdir insight_engine_streamlit_reports
if not exist media_engine_streamlit_reports mkdir media_engine_streamlit_reports
if not exist query_engine_streamlit_reports mkdir query_engine_streamlit_reports
echo √ 目录创建完成
echo.

REM 检查配置文件
if not exist config.py (
    echo 警告: config.py 不存在
    echo 系统将使用默认配置，你可以通过网页界面配置所有参数
)

echo.
echo ==========================================
echo   部署完成！
echo ==========================================
echo.
echo 启动方式：
echo.
if /i "%CREATE_VENV%"=="Y" (
    echo 1. 激活虚拟环境（如果未激活）：
    echo    venv\Scripts\activate.bat
    echo.
)
echo 2. 启动应用：
echo    python app.py
echo.
echo 3. 打开浏览器访问：
echo    http://localhost:5000
echo.
echo 4. 点击右上角 '⚙️ 配置' 按钮进行配置
echo.
echo 提示：
echo - 所有配置（包括数据库）都可以通过网页界面完成
echo - 配置会自动保存在浏览器本地
echo - 支持配置导出/导入和 WebDAV 云备份
echo.
echo 快速启动脚本已创建: start.bat
echo 下次可以直接运行: start.bat
echo.
pause
