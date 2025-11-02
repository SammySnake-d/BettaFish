#!/bin/bash
# 一键杀死所有 Agent 进程的脚本
# 用于在更新代码前清理所有运行中的服务

echo "========================================="
echo "开始停止所有 Agent 进程..."
echo "========================================="

# 定义所有使用的端口
PORTS=(5000 8501 8502 8503 8601 8602 8603)

# 记录被杀死的进程数
KILLED_COUNT=0

# 遍历所有端口，查找并杀死对应进程
for PORT in "${PORTS[@]}"; do
    echo ""
    echo "检查端口 $PORT..."
    
    # 查找占用该端口的进程 PID
    if command -v lsof &> /dev/null; then
        # 使用 lsof 命令（适用于大多数 Unix/Linux 系统）
        PIDS=$(lsof -ti:$PORT 2>/dev/null)
    elif command -v netstat &> /dev/null; then
        # 使用 netstat 作为备选方案
        PIDS=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
    else
        # 使用 ss 命令作为最后的备选方案
        PIDS=$(ss -tlnp 2>/dev/null | grep ":$PORT " | sed -n 's/.*pid=\([0-9]*\).*/\1/p')
    fi
    
    if [ -z "$PIDS" ]; then
        echo "  ✓ 端口 $PORT 没有运行的进程"
    else
        for PID in $PIDS; do
            if [ ! -z "$PID" ]; then
                # 获取进程信息
                PROCESS_INFO=$(ps -p $PID -o comm= 2>/dev/null)
                echo "  ⚠ 发现进程: PID=$PID, 名称=$PROCESS_INFO"
                
                # 尝试优雅地终止进程
                echo "  → 正在终止进程 $PID (SIGTERM)..."
                kill $PID 2>/dev/null
                
                # 等待进程终止
                sleep 2
                
                # 检查进程是否还在运行
                if ps -p $PID > /dev/null 2>&1; then
                    echo "  → 进程未响应，强制杀死 (SIGKILL)..."
                    kill -9 $PID 2>/dev/null
                    sleep 1
                fi
                
                # 验证进程是否已被杀死
                if ps -p $PID > /dev/null 2>&1; then
                    echo "  ✗ 无法杀死进程 $PID"
                else
                    echo "  ✓ 进程 $PID 已成功终止"
                    KILLED_COUNT=$((KILLED_COUNT + 1))
                fi
            fi
        done
    fi
done

# 额外检查：通过进程名查找相关的 Streamlit 和 Flask 进程
echo ""
echo "========================================="
echo "检查残留的 Streamlit 和 Flask 进程..."
echo "========================================="

# 查找所有 streamlit 进程
STREAMLIT_PIDS=$(pgrep -f "streamlit.*run" 2>/dev/null)
if [ ! -z "$STREAMLIT_PIDS" ]; then
    echo "发现 Streamlit 进程:"
    for PID in $STREAMLIT_PIDS; do
        PROCESS_INFO=$(ps -p $PID -o args= 2>/dev/null | head -c 80)
        echo "  ⚠ PID=$PID: $PROCESS_INFO"
        echo "  → 正在终止进程 $PID..."
        kill $PID 2>/dev/null
        sleep 1
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID 2>/dev/null
        fi
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "  ✓ 进程 $PID 已终止"
            KILLED_COUNT=$((KILLED_COUNT + 1))
        fi
    done
else
    echo "  ✓ 没有残留的 Streamlit 进程"
fi

# 查找所有相关的 Python Flask 进程
FLASK_PIDS=$(pgrep -f "python.*app\.py" 2>/dev/null)
if [ ! -z "$FLASK_PIDS" ]; then
    echo "发现 Flask 进程:"
    for PID in $FLASK_PIDS; do
        PROCESS_INFO=$(ps -p $PID -o args= 2>/dev/null | head -c 80)
        echo "  ⚠ PID=$PID: $PROCESS_INFO"
        echo "  → 正在终止进程 $PID..."
        kill $PID 2>/dev/null
        sleep 1
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID 2>/dev/null
        fi
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "  ✓ 进程 $PID 已终止"
            KILLED_COUNT=$((KILLED_COUNT + 1))
        fi
    done
else
    echo "  ✓ 没有残留的 Flask 进程"
fi

echo ""
echo "========================================="
echo "清理完成！"
echo "共终止 $KILLED_COUNT 个进程"
echo "========================================="
echo ""
echo "提示: 现在可以安全地更新代码并重新启动应用"
echo ""
