#!/bin/bash

# 微舆 (BettaFish) 一键部署脚本
# 支持 Linux 和 macOS

set -e

echo "=========================================="
echo "  微舆 (BettaFish) 一键部署脚本"
echo "=========================================="
echo ""

# 检查 Python 版本
echo "检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "错误: 未找到 Python。请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "找到 Python $PYTHON_VERSION"

# 检查 Python 版本是否 >= 3.8
REQUIRED_VERSION="3.8"
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "错误: Python 版本需要 >= 3.8，当前版本: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python 版本满足要求"
echo ""

# 询问是否创建虚拟环境
echo "是否创建 Python 虚拟环境? (推荐) [Y/n]"
read -r CREATE_VENV
CREATE_VENV=${CREATE_VENV:-Y}

if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    echo "创建虚拟环境..."
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        echo "✓ 虚拟环境创建成功"
    else
        echo "✓ 虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
    PYTHON_CMD=python
else
    echo "跳过虚拟环境创建"
fi

echo ""

# 升级 pip
echo "升级 pip..."
$PYTHON_CMD -m pip install --upgrade pip -q
echo "✓ pip 已升级"
echo ""

# 安装依赖
echo "安装 Python 依赖包..."
echo "这可能需要几分钟时间，请耐心等待..."
if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r requirements.txt -q
    echo "✓ Python 依赖包安装完成"
else
    echo "错误: requirements.txt 文件不存在"
    exit 1
fi

echo ""

# 安装 Playwright 浏览器
echo "安装 Playwright 浏览器..."
$PYTHON_CMD -m playwright install chromium
echo "✓ Playwright 浏览器安装完成"
echo ""

# 可选：安装 WebDAV 支持
echo "是否安装 WebDAV 云备份支持? [Y/n]"
read -r INSTALL_WEBDAV
INSTALL_WEBDAV=${INSTALL_WEBDAV:-Y}

if [[ "$INSTALL_WEBDAV" =~ ^[Yy]$ ]]; then
    echo "安装 WebDAV 支持..."
    $PYTHON_CMD -m pip install webdavclient3 -q
    echo "✓ WebDAV 支持已安装"
fi

echo ""

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs
mkdir -p reports
mkdir -p final_reports
mkdir -p insight_engine_streamlit_reports
mkdir -p media_engine_streamlit_reports
mkdir -p query_engine_streamlit_reports
echo "✓ 目录创建完成"
echo ""

# 检查配置文件
if [ ! -f "config.py" ]; then
    echo "警告: config.py 不存在"
    echo "系统将使用默认配置，你可以通过网页界面配置所有参数"
fi

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "启动方式："
echo ""
if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    echo "1. 激活虚拟环境（如果未激活）："
    echo "   source venv/bin/activate"
    echo ""
fi
echo "2. 启动应用："
echo "   $PYTHON_CMD app.py"
echo ""
echo "3. 打开浏览器访问："
echo "   http://localhost:5000"
echo ""
echo "4. 点击右上角 '⚙️ 配置' 按钮进行配置"
echo ""
echo "提示："
echo "- 所有配置（包括数据库）都可以通过网页界面完成"
echo "- 配置会自动保存在浏览器本地"
echo "- 支持配置导出/导入和 WebDAV 云备份"
echo ""
echo "快速启动脚本已创建: ./start.sh"
echo "下次可以直接运行: ./start.sh"
echo ""
