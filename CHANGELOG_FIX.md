# 修复说明：localhost 到动态主机地址 & 添加一键清理脚本

## 问题描述

用户通过服务器 IP 地址（如 `http://111.91.16.93:5000/`）访问系统时，遇到连接拒绝的问题。原因是前端页面存在硬编码的连接方式，不支持通过 IP 地址访问。

## 解决方案

### 1. 优化 Socket.IO 连接（`templates/index.html`）

**修改前：**
```javascript
socket = io();
```

**修改后：**
```javascript
// 动态构建Socket.IO连接URL，支持本地和远程部署
const socketUrl = `${window.location.protocol}//${window.location.hostname}:${window.location.port || (window.location.protocol === 'https:' ? 443 : 80)}`;
socket = io(socketUrl, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5
});
```

**优势：**
- 自动根据当前页面地址构建连接 URL
- 支持 HTTP 和 HTTPS 协议
- 支持本地（localhost）和远程（IP 地址）访问
- 添加重连机制，提高连接稳定性

### 2. 统一 Agent URL 构建方式

**添加通用函数：**
```javascript
const agentProtocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
const agentHostname = window.location.hostname || '127.0.0.1';

function buildAgentUrl(port, queryParams = {}) {
    const url = new URL(`${agentProtocol}//${agentHostname}:${port}`);
    Object.entries(queryParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            url.searchParams.set(key, value);
        }
    });
    return url.toString();
}
```

**替换所有硬编码的 URL：**
- iframe 预加载：`buildAgentUrl(port)`
- 搜索请求：`buildAgentUrl(ports[app], { query, auto_search: 'true' })`

### 3. 添加一键清理脚本

为了解决"部分 agent 没有删除导致重新运行错误"的问题，添加了三个跨平台脚本：

#### `kill_all_agents.sh`（Linux / macOS）
- 使用 `lsof`、`netstat` 或 `ss` 查找端口占用
- 优雅终止 → 强制终止
- 详细日志输出

#### `kill_all_agents.bat`（Windows）
- 使用 `netstat` 和 `taskkill`
- 强制终止所有相关进程
- 详细日志输出

#### `kill_all_agents.py`（跨平台，推荐）
- 使用 `psutil` 库
- 支持 Windows、Linux、macOS
- 功能最完善，错误处理最健全

**监控的端口：**
- 5000：Flask 主应用
- 8501：Insight Engine
- 8502：Media Engine
- 8503：Query Engine
- 8601-8603：API 端口

**查找的进程关键字：**
- streamlit
- app.py
- insight_engine
- media_engine
- query_engine

## 部署方式对比

| 部署方式 | Flask 监听地址 | 前端访问 | Socket.IO 连接 | Agent 访问 |
|---------|--------------|---------|---------------|-----------|
| 本地开发 | 0.0.0.0:5000 | http://localhost:5000 | localhost:5000 | localhost:8501-8503 |
| 局域网 | 0.0.0.0:5000 | http://192.168.1.100:5000 | 192.168.1.100:5000 | 192.168.1.100:8501-8503 |
| 公网 | 0.0.0.0:5000 | http://111.91.16.93:5000 | 111.91.16.93:5000 | 111.91.16.93:8501-8503 |

**注意：** `app.py` 已经配置为 `host='0.0.0.0'`（第 723 行），确保可以接受所有网络接口的连接。

## 使用指南

### 清理 Agent 进程

**Linux / macOS：**
```bash
./kill_all_agents.sh
```

**Windows：**
```cmd
kill_all_agents.bat
```

**跨平台（Python）：**
```bash
python kill_all_agents.py
```

### 重新启动应用

```bash
# 1. 清理旧进程
./kill_all_agents.sh

# 2. 启动应用
python app.py
```

## 更新内容

### 文件修改
- `templates/index.html`：优化 Socket.IO 连接，统一 URL 构建
- `requirements.txt`：添加 `psutil>=5.9.0`
- `README.md`：添加清理脚本使用说明

### 新增文件
- `kill_all_agents.sh`：Linux/macOS 清理脚本
- `kill_all_agents.bat`：Windows 清理脚本
- `kill_all_agents.py`：跨平台 Python 清理脚本
- `KILL_AGENTS_README.md`：详细使用文档
- `CHANGELOG_FIX.md`：本修复说明文档

## 验证

### 1. 测试本地访问
```bash
python app.py
# 浏览器访问：http://localhost:5000
```

### 2. 测试局域网访问
```bash
# 获取本机 IP
ifconfig  # Linux/macOS
ipconfig  # Windows

# 浏览器访问：http://<你的IP>:5000
```

### 3. 测试公网访问
```bash
# 确保防火墙开放端口 5000, 8501-8503
# 浏览器访问：http://<公网IP>:5000
```

### 4. 检查 Socket.IO 连接
打开浏览器开发者工具（F12）→ Console：
```
Socket.IO已连接到: http://<你的IP>:5000
```

### 5. 测试清理脚本
```bash
# 启动应用
python app.py &

# 清理所有进程
./kill_all_agents.sh

# 验证进程已清理
lsof -i :5000  # 应该没有输出
```

## 技术细节

### 为什么 Socket.IO 需要显式配置？

Socket.IO 默认行为：
- `io()`：连接到当前页面的 origin
- 当页面通过 IP 访问时，origin 是 IP 地址
- 某些浏览器或网络环境可能阻止这种连接

显式配置的好处：
- 明确指定连接地址
- 配置传输方式（websocket → polling 降级）
- 配置重连策略
- 更好的兼容性和稳定性

### URL 构建的最佳实践

使用 `URL` API 而不是字符串拼接：
```javascript
// 不推荐
const url = `http://${host}:${port}?query=${query}`;

// 推荐
const url = new URL(`http://${host}:${port}`);
url.searchParams.set('query', query);
return url.toString();
```

优势：
- 自动处理 URL 编码
- 避免注入攻击
- 更易维护

## 常见问题

### Q: 为什么访问 IP 地址还是显示拒绝连接？

**A:** 检查以下几点：
1. Flask 应用是否运行在 `0.0.0.0`（而不是 `127.0.0.1`）
2. 防火墙是否开放了端口 5000 和 8501-8503
3. 浏览器控制台是否有 CORS 错误
4. Socket.IO 是否成功连接（查看控制台日志）

### Q: 如何检查 Flask 监听地址？

**A:** 
```python
# app.py 第 723 行
socketio.run(app, host='0.0.0.0', port=5000, debug=False)
```

确保 `host='0.0.0.0'`，而不是 `'127.0.0.1'` 或 `'localhost'`。

### Q: 清理脚本提示"权限不足"怎么办？

**A:**
```bash
# Linux/macOS
sudo ./kill_all_agents.sh

# Windows
# 右键以管理员身份运行
```

### Q: 为什么有些进程杀不掉？

**A:** 可能原因：
1. 进程被其他程序占用
2. 权限不足
3. 进程处于僵尸状态

解决方案：
```bash
# 查看详细信息
ps aux | grep streamlit
ps aux | grep app.py

# 手动强制杀死
kill -9 <PID>
```

## 相关文档

- [KILL_AGENTS_README.md](./KILL_AGENTS_README.md)：清理脚本详细文档
- [README.md](./README.md)：项目主文档
- [app.py](./app.py)：Flask 主应用

## 兼容性

- **浏览器**：Chrome 60+, Firefox 55+, Safari 11+, Edge 79+
- **操作系统**：Windows 10+, Ubuntu 18.04+, macOS 10.14+
- **Python**：3.9+
- **依赖库**：psutil 5.9.0+

## 贡献者

感谢为这个问题提供反馈和测试的用户！

## 许可证

与项目主许可证一致。
