# 微舆系统启动指南

## ✅ 问题修复说明

### 1. API Key 可选启动 ✅

**修复内容**：
- ✅ 所有引擎现在都支持在没有 API Key 的情况下启动
- ✅ 启动时只显示警告，不会阻止系统运行
- ✅ 可以在启动后通过网页配置界面配置 API Key 并热更新

**之前的问题**：
```
错误: Report Engine LLM API Key 未设置 (REPORT_ENGINE_API_KEY)。
系统无法启动
```

**现在的行为**：
```
⚠️  警告: Report Engine LLM API Key 未设置，请在网页配置界面配置后使用。
系统正常启动 ✅
```

### 2. Werkzeug 生产环境警告 ✅

**修复内容**：
- ✅ 添加了 `allow_unsafe_werkzeug=True` 参数抑制警告
- ✅ 设置环境变量 `WERKZEUG_RUN_MAIN=true`
- ✅ 在代码中添加了生产部署建议

**生产环境建议**：

对于生产环境部署，推荐使用专业的 WSGI 服务器：

```bash
# 使用 gunicorn + eventlet (推荐)
pip install gunicorn eventlet
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 app:app

# 或使用 waitress
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

但对于开发和小规模部署，当前的配置已经足够。

## 🚀 快速启动

### 最简启动方式

```bash
# 1. 启动系统（无需任何配置）
python app.py

# 2. 打开浏览器
http://localhost:5000

# 3. 点击配置按钮
# 在网页界面配置所有 API Key

# 4. 开始使用
```

### 推荐启动流程

#### 步骤 1: 配置数据库（可选）

如果需要使用 Insight Engine 和 MindSpider 爬虫，需要配置数据库：

```bash
# 编辑 config.py
nano config.py

# 配置数据库信息
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "weiyu_user"
DB_PASSWORD = "your_password"
DB_NAME = "weiyu_db"
```

#### 步骤 2: 启动系统

```bash
python app.py
```

**启动日志示例**：

```
正在启动Streamlit应用...
停止ForumEngine监控器以避免文件冲突...
检查文件: SingleEngineApp/insight_engine_streamlit_app.py
启动 insight...
insight: 启动成功，端口: 8501
...
ForumEngine: 启动论坛...
初始化ReportEngine...
⚠️  警告: Report Engine LLM API Key 未设置，请在网页配置界面配置后使用。
Report Engine: 检测到缺少 LLM 配置，暂时跳过初始化。请在网页配置界面配置后再使用。
启动Flask服务器...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

#### 步骤 3: 网页配置

1. 打开浏览器访问：http://localhost:5000
2. 点击右上角 **⚙️ 配置** 按钮
3. 配置各引擎：
   - Insight Engine (Kimi)
   - Media Engine (Gemini)
   - Query Engine (DeepSeek)
   - Report Engine (Gemini)
   - Forum Host (Qwen)
   - Keyword Optimizer (Qwen)
4. 配置搜索工具：
   - Tavily API Key
   - Bocha API Key
5. 点击 **保存配置**

#### 步骤 4: 开始使用

配置保存后，所有组件自动热更新，即可开始使用。

## 📋 启动检查清单

### 必需项

- [ ] Python 3.8+ 已安装
- [ ] 依赖包已安装：`pip install -r requirements.txt`
- [ ] 端口可用：5000, 8501, 8502, 8503

### 可选项

- [ ] MySQL 数据库已配置（用于 Insight Engine）
- [ ] config.py 中的 DB_* 配置（如需使用数据库）
- [ ] LLM API Key（可启动后网页配置）

## ⚙️ 配置验证模式

### 宽松模式（启动时，默认）

```python
config.validate(strict=False)
```

- ✅ 允许缺少 API Key
- ✅ 只显示警告
- ✅ 系统正常启动
- ⚠️  使用时会提示配置

### 严格模式（使用时）

```python
config.validate(strict=True)
```

- ❌ 必须有完整配置
- ❌ 缺少配置会报错
- ✅ 保证功能正常运行

## 🔧 各引擎配置状态

### Insight Engine

**启动要求**：
- 宽松：只需数据库配置
- 严格：需要 LLM API Key + 数据库配置

**配置提示**：
```
⚠️  警告: Insight Engine LLM API Key 未设置，请在网页配置界面配置后使用。
⚠️  警告: 数据库连接信息不完整，请在 config.py 中配置 DB_*。
```

### Media Engine

**启动要求**：
- 宽松：无要求
- 严格：需要 LLM API Key + Bocha API Key

**配置提示**：
```
⚠️  警告: Media Engine LLM API Key 未设置，请在网页配置界面配置后使用。
⚠️  警告: Bocha API Key 未设置，请在网页配置界面配置后使用。
```

### Query Engine

**启动要求**：
- 宽松：无要求
- 严格：需要 LLM API Key + Tavily API Key

**配置提示**：
```
⚠️  警告: Query Engine LLM API Key 未设置，请在网页配置界面配置后使用。
⚠️  警告: Tavily API Key 未设置，请在网页配置界面配置后使用。
```

### Report Engine

**启动要求**：
- 宽松：无要求（会跳过初始化）
- 严格：需要 LLM API Key

**配置提示**：
```
⚠️  警告: Report Engine LLM API Key 未设置，请在网页配置界面配置后使用。
Report Engine: 检测到缺少 LLM 配置，暂时跳过初始化。请在网页配置界面配置后再使用。
```

**特殊处理**：
- 如果没有配置，`report_agent = None`
- 尝试使用时会提示需要配置
- 配置后可以重新初始化

### Forum Host 和 Keyword Optimizer

**启动要求**：
- 宽松：无要求（延迟初始化）
- 严格：需要 LLM API Key

**配置提示**：
```
⚠️  警告: Forum Host LLM API Key 未设置，请在网页配置界面配置后使用。
```

## 🔄 热更新机制

配置保存后的更新流程：

```
网页保存配置
   ↓
更新环境变量
   ↓
重新初始化 ReportEngine
   ↓
重置 ForumHost 实例
   ↓
配置立即生效 ✅
```

**支持热更新的组件**：
- ✅ ReportEngine
- ✅ ForumHost
- ✅ 所有 LLM 配置
- ✅ 所有搜索工具配置
- ✅ 所有高级参数

**不支持热更新**：
- ❌ 数据库配置（需要重启）
- ❌ Streamlit 子应用端口

## 🐛 故障排除

### 问题 1: 端口被占用

**错误信息**：
```
OSError: [Errno 48] Address already in use
```

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :5000
lsof -i :8501
lsof -i :8502
lsof -i :8503

# 终止进程
kill -9 <PID>

# 或使用不同的端口
export PORT=5001
python app.py
```

### 问题 2: 依赖包缺失

**错误信息**：
```
ModuleNotFoundError: No module named 'flask_socketio'
```

**解决方案**：
```bash
pip install -r requirements.txt

# 如果使用 WebDAV 备份功能
pip install webdavclient3

# 如果使用生产服务器
pip install gunicorn eventlet
```

### 问题 3: 数据库连接失败

**错误信息**：
```
⚠️  警告: 数据库连接信息不完整，请在 config.py 中配置 DB_*。
```

**解决方案**：
```bash
# 1. 检查 MySQL 服务是否运行
systemctl status mysql  # Linux
brew services list       # macOS

# 2. 验证数据库配置
mysql -h localhost -u weiyu_user -p

# 3. 确保数据库存在
mysql> CREATE DATABASE IF NOT EXISTS weiyu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题 4: Streamlit 子应用启动失败

**错误信息**：
```
insight: 启动失败
```

**解决方案**：
```bash
# 1. 检查文件是否存在
ls SingleEngineApp/insight_engine_streamlit_app.py

# 2. 手动测试启动
cd SingleEngineApp
streamlit run insight_engine_streamlit_app.py --server.port 8501

# 3. 查看详细错误日志
```

### 问题 5: 网页配置不生效

**症状**：
- 保存配置后仍然提示未配置
- 引擎无法使用

**解决方案**：
```bash
# 1. 检查浏览器 localStorage
# 打开浏览器控制台，执行：
localStorage.getItem('weiyu_llm_config')

# 2. 清除并重新配置
localStorage.removeItem('weiyu_llm_config')
# 然后重新在网页配置

# 3. 检查后端是否收到配置
# 查看终端日志，应该有：
# "配置已保存"
# "ReportEngine 已重新初始化"
```

## 📊 启动状态检查

### 服务端口状态

```bash
# 检查所有服务端口
netstat -an | grep LISTEN | grep -E '5000|8501|8502|8503'

# 预期输出
tcp4  0  0  *.5000   *.*  LISTEN   # Flask 主应用
tcp4  0  0  *.8501   *.*  LISTEN   # Insight Engine
tcp4  0  0  *.8502   *.*  LISTEN   # Media Engine
tcp4  0  0  *.8503   *.*  LISTEN   # Query Engine
```

### 网页访问测试

```bash
# 测试主页面
curl http://localhost:5000

# 测试配置 API
curl http://localhost:5000/api/config

# 测试 Streamlit 应用
curl http://localhost:8501
curl http://localhost:8502
curl http://localhost:8503
```

### 日志文件检查

```bash
# 查看主日志
tail -f logs/report.log

# 查看 Forum 日志
tail -f logs/forum.log

# 查看配置状态
cat logs/report_baseline.json
```

## 🎯 不同使用场景的启动方式

### 场景 1: 快速测试（无需任何配置）

```bash
python app.py
# 打开 http://localhost:5000
# 直接浏览界面，暂不进行分析
```

### 场景 2: 联网搜索分析（Query + Media）

```bash
# 1. 启动系统
python app.py

# 2. 配置以下 API Key:
# - Query Engine API Key
# - Media Engine API Key
# - Tavily API Key
# - Bocha API Key

# 3. 开始搜索分析
```

### 场景 3: 历史数据分析（Insight）

```bash
# 1. 配置数据库
# 编辑 config.py 中的 DB_* 配置

# 2. 启动系统
python app.py

# 3. 配置 Insight Engine API Key

# 4. 分析历史舆情数据
```

### 场景 4: 完整分析（All Engines）

```bash
# 1. 配置数据库
# 2. 启动系统
python app.py

# 3. 配置所有 API Key
# 4. 进行全面舆情分析
```

### 场景 5: 生产部署

```bash
# 1. 使用环境变量配置
export DB_HOST=production-db
export DB_USER=prod_user
export DB_PASSWORD=secure_password

# 2. 使用生产服务器
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 --access-logfile - --error-logfile - app:app

# 3. 通过网页配置 LLM API
```

## 📚 相关文档

- `CONFIGURATION_GUIDE.md` - 完整配置指南
- `ADVANCED_CONFIG_GUIDE.md` - 高级配置和备份功能
- `CONFIGURATION_UNIFICATION.md` - 配置统一说明
- `WEB_CONFIG_GUIDE.md` - 网页配置使用指南

## ✨ 更新日志

### v2.0 (2025-01-10)

**新增**：
- ✅ 支持无 API Key 启动
- ✅ 所有引擎宽松模式验证
- ✅ 启动时只显示警告，不阻止运行
- ✅ Werkzeug 警告抑制

**改进**：
- ✅ 更友好的启动提示
- ✅ 明确的配置指引
- ✅ 热更新支持

---

**文档版本**: v2.0  
**最后更新**: 2025-01-10  
**维护者**: 微舆开发团队
