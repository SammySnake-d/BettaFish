# 微舆 (BettaFish) 一键部署指南

## 🚀 快速开始

### Windows 用户

1. **下载并解压项目**

2. **双击运行部署脚本**
   ```
   双击: deploy.bat
   ```

3. **按提示操作**
   - 选择是否创建虚拟环境（推荐选择 Y）
   - 选择是否安装 WebDAV 支持（推荐选择 Y）
   - 等待依赖安装完成

4. **启动应用**
   ```
   双击: start.bat
   ```
   或命令行执行：
   ```batch
   python app.py
   ```

5. **打开浏览器**
   ```
   访问: http://localhost:5000
   ```

### Linux/macOS 用户

1. **下载并解压项目**

2. **运行部署脚本**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **按提示操作**
   - 选择是否创建虚拟环境（推荐选择 Y）
   - 选择是否安装 WebDAV 支持（推荐选择 Y）
   - 等待依赖安装完成

4. **启动应用**
   ```bash
   ./start.sh
   ```
   或：
   ```bash
   # 如果使用了虚拟环境
   source venv/bin/activate
   python app.py
   ```

5. **打开浏览器**
   ```
   访问: http://localhost:5000
   ```

## ⚙️ 网页配置

### 首次配置流程

启动应用后，点击右上角的 **⚙️ 配置** 按钮，按以下顺序配置：

#### 1. LLM 引擎配置 🤖

配置各个引擎使用的大语言模型：

- **Insight Engine**（推荐 Kimi）
  - Base URL: `https://api.moonshot.cn/v1`
  - Model Name: `kimi-k2-0711-preview`
  - API Key: 你的 Kimi API Key

- **Media Engine**（推荐 Gemini）
  - Base URL: `https://www.chataiapi.com/v1`（或其他代理）
  - Model Name: `gemini-2.5-pro`
  - API Key: 你的 Gemini API Key

- **Query Engine**（推荐 DeepSeek）
  - Base URL: `https://api.deepseek.com`
  - Model Name: `deepseek-reasoner`
  - API Key: 你的 DeepSeek API Key

- **Report Engine**（推荐 Gemini）
  - 同 Media Engine 配置

- **Forum Host**（推荐 Qwen）
  - Base URL: `https://api.siliconflow.cn/v1`
  - Model Name: `Qwen/Qwen3-235B-A22B-Instruct-2507`
  - API Key: 你的硅基流动 API Key

- **Keyword Optimizer**（Qwen）
  - Base URL: `https://api.siliconflow.cn/v1`
  - Model Name: `Qwen/Qwen3-30B-A3B-Instruct-2507`
  - API Key: 你的硅基流动 API Key

#### 2. 检索工具配置 🔍

- **Tavily API Key**: 用于 Query Agent 的联网检索
  - 申请地址: https://www.tavily.com/

- **Bocha API Key**: 用于 Media Agent 的网页搜索
  - 申请地址: https://open.bochaai.com/

#### 3. 数据库配置 🗄️ （可选）

**注意**: 只有使用 Insight Engine 或 MindSpider 爬虫时才需要配置数据库。

- **数据库主机**: `localhost` 或 `127.0.0.1`
- **数据库端口**: `3306`
- **数据库用户名**: 例如 `weiyu_user`
- **数据库密码**: 你的数据库密码
- **数据库名称**: 例如 `weiyu_db`
- **字符集**: `utf8mb4`（推荐）

**没有 MySQL？**
- 安装 [XAMPP](https://www.apachefriends.org/)（Windows/Mac/Linux）
- 安装 [WAMP](https://www.wampserver.com/)（Windows）
- 使用云数据库（阿里云RDS、腾讯云等）

#### 4. 高级参数配置 ⚙️（可选）

根据需要调整各引擎的高级参数：
- Query Engine: 反思轮次、搜索结果数等
- Media Engine: 段落数等
- Insight Engine: 搜索限制、评论获取限制等

#### 5. 情感分析配置 💬（可选）

如果需要使用情感分析功能：
- 模型类型: `multilingual`（推荐）
- 置信度阈值: `0.8`
- 批处理大小: `32`
- 最大序列长度: `512`

#### 6. WebDAV 备份配置 ☁️（可选）

配置云备份功能：
- **坚果云示例**:
  - 服务器地址: `https://dav.jianguoyun.com/dav/`
  - 用户名: 你的坚果云账号
  - 密码: 坚果云应用密码（非登录密码）

### 保存和应用配置

1. 配置完成后点击 **保存配置**
2. 系统会自动：
   - 保存到浏览器本地（localStorage）
   - 应用到运行环境
   - 热更新相关组件

3. 配置会在刷新页面后自动加载

## 💾 配置管理

### 导出配置

1. 点击 **💾 导出到本地** 按钮
2. 下载 JSON 配置文件
3. 妥善保存配置文件

### 导入配置

1. 点击 **📂 从本地导入** 按钮
2. 选择之前导出的 JSON 文件
3. 确认导入

### WebDAV 云备份

1. 配置 WebDAV 服务器信息
2. 点击 **☁️ 备份到WebDAV** 按钮
3. 配置自动备份到云端 `BettaFish` 文件夹

### WebDAV 云恢复

1. 点击 **☁️ 从WebDAV恢复** 按钮
2. 自动选择最新备份
3. 确认恢复

### 恢复默认配置

点击 **恢复推荐配置** 按钮恢复所有参数到推荐值（不会清除 API Key）

## 🎯 使用场景

### 场景 1: 快速开始（最小配置）

只需配置：
- Query Engine（DeepSeek）
- Tavily API Key

即可使用基本的联网搜索分析功能。

### 场景 2: 完整体验（推荐配置）

配置所有 6 个引擎 + 2 个搜索工具，体验完整的多智能体协作分析。

### 场景 3: 历史数据分析

额外配置数据库，使用 Insight Engine 和 MindSpider 分析历史舆情数据。

## 📝 配置文件说明

### 自动生成的配置文件

- `logs/`: 日志目录
- `reports/`: 报告输出目录
- `final_reports/`: 最终报告目录
- `insight_engine_streamlit_reports/`: Insight Engine 报告
- `media_engine_streamlit_reports/`: Media Engine 报告
- `query_engine_streamlit_reports/`: Query Engine 报告

### 配置存储

- **浏览器 localStorage**: 主要配置存储位置
- **环境变量**: 运行时应用的配置
- **config.py**: 备用配置文件（可选）

### 配置优先级

```
网页配置（localStorage） > 环境变量 > config.py 默认值
```

## 🔧 故障排除

### Python 未找到

**Windows**:
1. 下载 Python: https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"

**macOS**:
```bash
brew install python3
```

**Linux**:
```bash
sudo apt-get install python3 python3-pip
```

### 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### 依赖安装失败

**解决**:
```bash
# 更新 pip
python -m pip install --upgrade pip

# 清除缓存重新安装
pip cache purge
pip install -r requirements.txt
```

### 数据库连接失败

**检查**:
1. MySQL 服务是否运行
2. 数据库名称是否存在
3. 用户名密码是否正确
4. 端口是否正确（默认 3306）

**创建数据库**:
```sql
CREATE DATABASE weiyu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 配置不生效

1. 检查浏览器控制台是否有错误
2. 清除浏览器 localStorage 重新配置
3. 检查后端日志是否有错误信息

## 📞 获取帮助

### 文档

- `CONFIGURATION_GUIDE.md` - 完整配置指南
- `ADVANCED_CONFIG_GUIDE.md` - 高级配置说明
- `STARTUP_GUIDE.md` - 启动问题解决
- `WEB_CONFIG_GUIDE.md` - 网页配置详解

### API 密钥申请

- **Kimi**: https://platform.moonshot.cn/
- **DeepSeek**: https://www.deepseek.com/
- **Gemini**: https://ai.google.dev/（或使用代理）
- **Qwen (硅基流动)**: https://cloud.siliconflow.cn/
- **Tavily**: https://www.tavily.com/
- **Bocha**: https://open.bochaai.com/

### 社区支持

- GitHub Issues
- 项目文档
- 技术论坛

## 🎉 开始使用

完成配置后，你就可以：

1. **开始分析**: 在主页面输入话题，选择引擎进行分析
2. **查看报告**: 在各引擎的页面查看生成的报告
3. **论坛讨论**: ForumEngine 自动组织智能体讨论
4. **生成总报告**: ReportEngine 整合所有分析结果

享受微舆带来的强大舆情分析能力！ 🚀

---

**文档版本**: v1.0  
**最后更新**: 2025-01-10  
**维护者**: 微舆开发团队
