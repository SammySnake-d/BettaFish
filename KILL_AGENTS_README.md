# 一键杀死所有 Agent 进程工具

## 概述

本工具用于快速停止所有运行中的 Agent 进程，包括：
- Flask 主应用 (端口 5000)
- Insight Engine (端口 8501)
- Media Engine (端口 8502)
- Query Engine (端口 8503)
- 以及其他相关的 Streamlit 和 Python 进程

## 使用场景

- 更新代码前需要清理所有进程
- 部分 Agent 没有正常关闭导致端口被占用
- 重新部署应用前进行环境清理
- 调试过程中需要完全重启所有服务

## 使用方法

根据您的操作系统选择合适的脚本：

### Linux / macOS

#### 方式一：使用 Bash 脚本（推荐）

```bash
# 进入项目目录
cd /path/to/project

# 运行脚本
./kill_all_agents.sh
```

#### 方式二：使用 Python 脚本

```bash
# 确保已安装 psutil
pip install psutil

# 运行脚本
python3 kill_all_agents.py
# 或者
./kill_all_agents.py
```

### Windows

#### 方式一：使用批处理脚本

双击 `kill_all_agents.bat` 或在命令提示符中运行：

```cmd
kill_all_agents.bat
```

#### 方式二：使用 Python 脚本

```cmd
# 确保已安装 psutil
pip install psutil

# 运行脚本
python kill_all_agents.py
```

### 跨平台（推荐）

Python 脚本支持所有平台（Windows、Linux、macOS）：

```bash
python kill_all_agents.py
```

## 脚本说明

### kill_all_agents.sh (Linux/macOS)
- 使用 `lsof`、`netstat` 或 `ss` 命令查找占用端口的进程
- 通过进程名查找残留的 Streamlit 和 Flask 进程
- 先尝试优雅终止 (SIGTERM)，如果失败则强制终止 (SIGKILL)
- 显示详细的终止日志

### kill_all_agents.bat (Windows)
- 使用 `netstat` 查找占用端口的进程
- 使用 `tasklist` 和 `taskkill` 管理进程
- 强制终止所有找到的进程
- 显示详细的终止日志

### kill_all_agents.py (跨平台)
- 使用 `psutil` 库进行跨平台进程管理
- 支持 Windows、Linux 和 macOS
- 功能最完善，错误处理最健全
- 先尝试优雅终止，失败后再强制终止
- 提供最详细的进程信息和终止日志

## 监控的端口

脚本会检查并清理以下端口上的进程：

| 端口 | 用途 |
|-----|------|
| 5000 | Flask 主应用 |
| 8501 | Insight Engine (Streamlit) |
| 8502 | Media Engine (Streamlit) |
| 8503 | Query Engine (Streamlit) |
| 8601 | Insight Engine API |
| 8602 | Media Engine API |
| 8603 | Query Engine API |

## 查找的进程关键字

除了端口检查，脚本还会根据以下关键字查找相关进程：

- `streamlit`
- `app.py`
- `insight_engine`
- `media_engine`
- `query_engine`

## 注意事项

### 权限要求
- **Linux/macOS**: 可能需要 `sudo` 权限来终止某些进程
- **Windows**: 可能需要以管理员身份运行

### 数据安全
- 脚本会强制终止进程，可能导致未保存的数据丢失
- 建议在确认所有重要数据已保存后再运行

### 误杀风险
- 脚本会终止所有匹配条件的进程
- 如果您同时运行了其他 Streamlit 应用，它们也会被终止
- 请确认您要终止的进程

## 故障排除

### 问题：脚本无法执行

**Linux/macOS**:
```bash
chmod +x kill_all_agents.sh
chmod +x kill_all_agents.py
```

**Windows**: 右键 -> 以管理员身份运行

### 问题：找不到 psutil 模块

```bash
# 安装 psutil
pip install psutil

# 或者安装项目所有依赖
pip install -r requirements.txt
```

### 问题：进程无法终止

**Linux/macOS**:
```bash
# 使用 sudo 运行
sudo ./kill_all_agents.sh
# 或
sudo python3 kill_all_agents.py
```

**Windows**: 以管理员身份运行命令提示符或 PowerShell

### 问题：端口仍被占用

如果脚本运行后端口仍被占用，可以手动检查：

**Linux/macOS**:
```bash
# 查看端口占用
lsof -i :5000
lsof -i :8501
lsof -i :8502
lsof -i :8503

# 手动终止进程
kill -9 <PID>
```

**Windows**:
```cmd
# 查看端口占用
netstat -ano | findstr :5000
netstat -ano | findstr :8501

# 手动终止进程
taskkill /PID <PID> /F
```

## 示例输出

```
=========================================
开始停止所有 Agent 进程...
=========================================

检查端口 5000...
  ⚠ 发现进程: PID=12345, 名称=python
  → 正在终止进程 12345 (SIGTERM)...
  ✓ 进程 12345 已成功终止

检查端口 8501...
  ⚠ 发现进程: PID=12346, 名称=python
  → 正在终止进程 12346 (SIGTERM)...
  ✓ 进程 12346 已成功终止

检查端口 8502...
  ✓ 端口 8502 没有运行的进程

=========================================
检查残留的 Streamlit 和 Flask 进程...
=========================================
  ✓ 没有残留的 Streamlit 进程
  ✓ 没有残留的 Flask 进程

=========================================
清理完成！
共终止 2 个进程
=========================================

提示: 现在可以安全地更新代码并重新启动应用
```

## 常见工作流

### 完整重启流程

1. 停止所有 Agent：
   ```bash
   ./kill_all_agents.sh
   # 或
   python kill_all_agents.py
   ```

2. 更新代码（如果需要）：
   ```bash
   git pull origin main
   ```

3. 重新启动应用：
   ```bash
   python app.py
   ```

### 快速清理流程

如果只是想清理环境而不重启：

```bash
./kill_all_agents.sh && echo "清理完成，可以开始新的工作了"
```

## 高级用法

### 只终止特定端口的进程

如果只想终止特定端口，可以手动编辑脚本中的 `PORTS` 变量。

例如，在 Python 脚本中：

```python
# 只清理 Flask 主应用
PORTS = [5000]
```

### 与 CI/CD 集成

可以将这些脚本集成到 CI/CD 流程中：

```yaml
# 示例：GitHub Actions
- name: Clean up existing processes
  run: |
    python kill_all_agents.py
    
- name: Start application
  run: |
    python app.py &
```

## 技术细节

### Bash 脚本实现
- 使用 `lsof -ti:PORT` 查找进程
- 备选方案：`netstat` 和 `ss`
- 信号处理：先 SIGTERM，后 SIGKILL
- 延时等待确保进程完全终止

### Python 脚本实现
- 使用 `psutil` 库进行跨平台进程管理
- `net_connections()` 查找端口占用
- `process_iter()` 遍历所有进程
- 异常处理确保脚本健壮性

### Windows 批处理实现
- 使用 `netstat -ano` 查找进程
- 使用 `taskkill /F` 强制终止
- 使用 `findstr` 过滤进程

## 贡献

如果您发现任何问题或有改进建议，欢迎提交 Issue 或 Pull Request。

## 许可证

本工具遵循项目主许可证。
