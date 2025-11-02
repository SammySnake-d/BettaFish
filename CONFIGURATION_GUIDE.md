# 微舆系统配置完全指南

## 📖 目录

- [1. 系统架构与配置概述](#1-系统架构与配置概述)
- [2. 配置方式](#2-配置方式)
- [3. 核心配置说明](#3-核心配置说明)
- [4. 各引擎配置详解](#4-各引擎配置详解)
- [5. MindSpider爬虫配置](#5-mindspider爬虫配置)
- [6. 配置最佳实践](#6-配置最佳实践)
- [7. 常见问题](#7-常见问题)

---

## 1. 系统架构与配置概述

### 1.1 系统是运行时服务

✅ **微舆系统采用运行时服务模式**，不是单次启动后结束的程序。

- **Flask 应用**：持续运行在 `0.0.0.0:5000`
- **WebSocket 服务**：通过 Flask-SocketIO 提供实时通信
- **Streamlit 子应用**：3个引擎的独立UI运行在不同端口
  - Insight Engine: 8501
  - Media Engine: 8502
  - Query Engine: 8503
- **ForumEngine 监控**：后台线程持续监控日志文件
- **ReportEngine**：待命状态，按需生成报告

系统启动后会持续运行，直到手动停止（Ctrl+C）。

### 1.2 配置文件结构

```
/home/engine/project/
├── config.py                    # 🔧 主配置文件（统一配置入口）
├── MindSpider/
│   └── config.py               # 🔗 MindSpider配置（现已统一到主配置）
├── InsightEngine/utils/
│   └── config.py               # 📋 InsightEngine配置加载器
├── MediaEngine/utils/
│   └── config.py               # 📋 MediaEngine配置加载器
├── QueryEngine/utils/
│   └── config.py               # 📋 QueryEngine配置加载器
└── ReportEngine/utils/
    └── config.py               # 📋 ReportEngine配置加载器
```

**说明**：
- **主配置文件** (`/config.py`)：所有配置的唯一来源
- **引擎配置加载器**：各引擎从主配置文件读取配置
- **MindSpider配置**：已统一从主配置导入，无需单独配置

---

## 2. 配置方式

### 2.1 推荐方式：网页可视化配置 ⭐

**最简单、最推荐的配置方式！**

1. 访问微舆主页面
2. 点击右上角 **⚙️ 配置** 按钮
3. 填写各引擎的配置信息
4. 点击 **保存配置**

**优势**：
- ✅ 可视化界面，无需编辑代码
- ✅ 保存后立即生效，无需重启
- ✅ 配置保存在浏览器本地，永久保存
- ✅ 自动填充推荐的默认值
- ✅ 支持快速恢复推荐配置

**配置存储位置**：浏览器 localStorage

**配置优先级**：最高（覆盖文件配置和环境变量）

### 2.2 方式二：编辑配置文件

编辑 `/home/engine/project/config.py` 文件，修改相应的配置项。

```python
# 例如修改 Insight Engine 配置
INSIGHT_ENGINE_API_KEY = "your_actual_api_key"
INSIGHT_ENGINE_BASE_URL = "https://api.moonshot.cn/v1"
INSIGHT_ENGINE_MODEL_NAME = "kimi-k2-0711-preview"
```

**优势**：
- 适合批量配置
- 适合服务器环境
- 配置版本可控（可提交到 Git）

**配置优先级**：最低（作为默认值）

### 2.3 方式三：环境变量

通过设置环境变量来配置系统。

```bash
export INSIGHT_ENGINE_API_KEY="your_api_key"
export INSIGHT_ENGINE_BASE_URL="https://api.moonshot.cn/v1"
export INSIGHT_ENGINE_MODEL_NAME="kimi-k2-0711-preview"
```

或在 Docker/Docker Compose 中：

```yaml
environment:
  - INSIGHT_ENGINE_API_KEY=your_api_key
  - INSIGHT_ENGINE_BASE_URL=https://api.moonshot.cn/v1
```

**优势**：
- 适合容器化部署
- 敏感信息不入代码库
- 方便CI/CD流程

**配置优先级**：中等（覆盖文件配置，但被网页配置覆盖）

### 2.4 配置优先级总结

```
网页配置 (localStorage) > 环境变量 > 配置文件 (config.py)
   最高优先级           中等优先级        最低优先级（默认值）
```

---

## 3. 核心配置说明

### 3.1 数据库配置 🗄️

**必须配置项**，用于连接MySQL数据库存储爬虫数据和分析结果。

| 配置项 | 说明 | 默认值 | 配置方式 |
|--------|------|--------|----------|
| `DB_HOST` | 数据库主机地址 | `your_db_host` | 仅支持文件/环境变量 |
| `DB_PORT` | 数据库端口 | `3306` | 仅支持文件/环境变量 |
| `DB_USER` | 数据库用户名 | `your_db_user` | 仅支持文件/环境变量 |
| `DB_PASSWORD` | 数据库密码 | `your_db_password` | 仅支持文件/环境变量 |
| `DB_NAME` | 数据库名称 | `your_db_name` | 仅支持文件/环境变量 |
| `DB_CHARSET` | 字符集 | `utf8mb4` | 仅支持文件/环境变量 |

**⚠️ 注意**：
- 数据库配置**不支持网页配置**（安全考虑）
- 必须在 `config.py` 文件或环境变量中配置
- MindSpider 爬虫和 InsightEngine 都使用此数据库配置

**配置示例**：

```python
# config.py
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "weiyu_user"
DB_PASSWORD = "your_secure_password"
DB_NAME = "weiyu_db"
DB_CHARSET = "utf8mb4"
```

---

## 4. 各引擎配置详解

### 4.1 Insight Engine（私有数据库挖掘）🔍

**功能**：从私有舆情数据库中挖掘和分析历史数据，进行模式对比和深度分析。

**配置项**：

| 配置项 | 说明 | 推荐值 | 网页配置 |
|--------|------|--------|----------|
| `INSIGHT_ENGINE_API_KEY` | LLM API密钥 | 从 Kimi 申请 | ✅ 支持 |
| `INSIGHT_ENGINE_BASE_URL` | API地址 | `https://api.moonshot.cn/v1` | ✅ 支持 |
| `INSIGHT_ENGINE_MODEL_NAME` | 模型名称 | `kimi-k2-0711-preview` | ✅ 支持 |

**推荐配置**：
- **服务商**：Moonshot Kimi
- **申请地址**：https://platform.moonshot.cn/
- **推荐原因**：超长上下文（128K），适合处理大量历史数据
- **模型特点**：擅长深度分析和逻辑推理

**配置说明**：
- 需要足够的上下文长度处理数据库查询结果
- 建议使用支持长文本的模型
- 数据库查询依赖 `DB_*` 配置

---

### 4.2 Media Engine（多模态内容分析）📸

**功能**：分析媒体报道、图片、视频等多模态内容，评估视觉信息的传播效果。

**配置项**：

| 配置项 | 说明 | 推荐值 | 网页配置 |
|--------|------|--------|----------|
| `MEDIA_ENGINE_API_KEY` | LLM API密钥 | 从服务商申请 | ✅ 支持 |
| `MEDIA_ENGINE_BASE_URL` | API地址 | `https://www.chataiapi.com/v1` | ✅ 支持 |
| `MEDIA_ENGINE_MODEL_NAME` | 模型名称 | `gemini-2.5-pro` | ✅ 支持 |

**推荐配置**：
- **服务商**：Google Gemini（通过中转服务）
- **申请地址**：https://www.chataiapi.com/
- **推荐原因**：原生支持多模态，图文理解能力强
- **模型特点**：擅长处理图片、视频等视觉内容

**配置说明**：
- 建议使用支持多模态的模型
- 需要配合 Bocha API 使用（见搜索工具配置）
- 处理图文混合的社交媒体内容

---

### 4.3 Query Engine（精准信息搜索）🔎

**功能**：负责精准信息搜索，提供最新的网络信息和实时动态。

**配置项**：

| 配置项 | 说明 | 推荐值 | 网页配置 |
|--------|------|--------|----------|
| `QUERY_ENGINE_API_KEY` | LLM API密钥 | 从 DeepSeek 申请 | ✅ 支持 |
| `QUERY_ENGINE_BASE_URL` | API地址 | `https://api.deepseek.com` | ✅ 支持 |
| `QUERY_ENGINE_MODEL_NAME` | 模型名称 | `deepseek-reasoner` | ✅ 支持 |

**推荐配置**：
- **服务商**：DeepSeek
- **申请地址**：https://www.deepseek.com/
- **推荐原因**：强大的推理能力，性价比高
- **模型特点**：擅长复杂推理和搜索查询优化

**配置说明**：
- 需要配合 Tavily API 使用（见搜索工具配置）
- 负责生成和优化搜索查询
- 处理联网搜索结果并生成报告

---

### 4.4 Report Engine（最终报告生成）📝

**功能**：整合所有引擎的分析结果，生成综合性的HTML报告。

**配置项**：

| 配置项 | 说明 | 推荐值 | 网页配置 |
|--------|------|--------|----------|
| `REPORT_ENGINE_API_KEY` | LLM API密钥 | 从服务商申请 | ✅ 支持 |
| `REPORT_ENGINE_BASE_URL` | API地址 | `https://www.chataiapi.com/v1` | ✅ 支持 |
| `REPORT_ENGINE_MODEL_NAME` | 模型名称 | `gemini-2.5-pro` | ✅ 支持 |

**推荐配置**：
- **服务商**：Google Gemini（通过中转服务）
- **申请地址**：https://www.chataiapi.com/
- **推荐原因**：综合能力强，生成报告质量高
- **模型特点**：擅长整合多源信息，生成结构化报告

**配置说明**：
- 负责最终报告的生成和优化
- 需要处理来自3个引擎的输出
- 支持自定义报告模板

---

### 4.5 Forum Host（多智能体主持人）🎙️

**功能**：作为论坛主持人，引导多个Agent进行讨论，整合不同视角。

**配置项**：

| 配置项 | 说明 | 推荐值 | 网页配置 |
|--------|------|--------|----------|
| `FORUM_HOST_API_KEY` | LLM API密钥 | 从硅基流动申请 | ✅ 支持 |
| `FORUM_HOST_BASE_URL` | API地址 | `https://api.siliconflow.cn/v1` | ✅ 支持 |
| `FORUM_HOST_MODEL_NAME` | 模型名称 | `Qwen/Qwen3-235B-A22B-Instruct-2507` | ✅ 支持 |

**推荐配置**：
- **服务商**：硅基流动（SiliconFlow）
- **申请地址**：https://cloud.siliconflow.cn/
- **推荐原因**：大参数Qwen模型，综合协调能力强
- **模型特点**：擅长多角度分析和观点整合

**配置说明**：
- 监控三个引擎的输出日志
- 生成主持人发言，引导讨论方向
- 需要较强的理解和总结能力

---

### 4.6 Keyword Optimizer（SQL关键词优化）🔧

**功能**：优化Agent生成的搜索词，使其更适合舆情数据库查询。

**配置项**：

| 配置项 | 说明 | 推荐值 | 网页配置 |
|--------|------|--------|----------|
| `KEYWORD_OPTIMIZER_API_KEY` | LLM API密钥 | 从硅基流动申请 | ✅ 支持 |
| `KEYWORD_OPTIMIZER_BASE_URL` | API地址 | `https://api.siliconflow.cn/v1` | ✅ 支持 |
| `KEYWORD_OPTIMIZER_MODEL_NAME` | 模型名称 | `Qwen/Qwen3-30B-A3B-Instruct-2507` | ✅ 支持 |

**推荐配置**：
- **服务商**：硅基流动（SiliconFlow）
- **申请地址**：https://cloud.siliconflow.cn/
- **推荐原因**：小参数模型，响应快，成本低
- **模型特点**：专注于关键词提取和优化

**配置说明**：
- 将专业术语转换为网民常用词汇
- 优化数据库查询的关键词
- 提高搜索结果的准确性

---

## 5. MindSpider爬虫配置

### 5.1 配置统一说明

**重要变更**：MindSpider 的配置已统一到主配置文件。

- **旧方式**：在 `MindSpider/config.py` 单独配置
- **新方式**：自动从 `/config.py` 导入配置
- **优势**：配置统一管理，避免重复配置

### 5.2 数据库配置

MindSpider 使用与主系统相同的数据库配置：

```python
# 自动使用主配置文件中的：
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
DB_CHARSET
```

**说明**：
- 爬虫数据存储在配置的MySQL数据库中
- InsightEngine 从同一数据库读取数据
- 确保数据库已正确初始化

### 5.3 DeepSeek API配置

MindSpider 的某些功能（如话题提取）需要 DeepSeek API：

| 配置项 | 说明 | 来源 | 网页配置 |
|--------|------|------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 环境变量或自动使用Query Engine配置 | ✅ 间接支持 |

**自动配置逻辑**：
1. 首先查找环境变量 `DEEPSEEK_API_KEY`
2. 如果未设置，自动使用 `QUERY_ENGINE_API_KEY`（如果Query Engine使用DeepSeek）
3. 可通过网页配置 Query Engine 来间接配置

### 5.4 爬虫平台配置

MindSpider 支持以下平台爬取：

| 平台 | 代码 | 说明 |
|------|------|------|
| 小红书 | `xhs` | 图文社交平台 |
| 抖音 | `dy` | 短视频平台 |
| 快手 | `ks` | 短视频平台 |
| 哔哩哔哩 | `bili` | 视频弹幕网站 |
| 微博 | `wb` | 微博客平台 |
| 百度贴吧 | `tieba` | 论坛社区 |
| 知乎 | `zhihu` | 问答社区 |

**配置说明**：
- 各平台的具体配置在 `MindSpider/DeepSentimentCrawling/MediaCrawler/config/` 目录
- 登录方式、爬取数量等参数可在运行时指定
- 默认使用无头浏览器模式

---

## 6. 搜索工具配置

### 6.1 Tavily Search API 🌐

**用途**：Query Engine 的联网搜索能力

| 配置项 | 说明 | 申请地址 | 网页配置 |
|--------|------|----------|----------|
| `TAVILY_API_KEY` | Tavily API密钥 | https://www.tavily.com/ | ✅ 支持 |

**功能**：
- 实时网络搜索
- 获取最新新闻和资讯
- 支持多种搜索模式

**配置说明**：
- Query Engine 必需
- 免费套餐有调用限制
- 付费套餐提供更高配额

### 6.2 Bocha Web Search API 🔍

**用途**：Media Engine 的网页搜索与多模态分析

| 配置项 | 说明 | 申请地址 | 网页配置 |
|--------|------|----------|----------|
| `BOCHA_WEB_SEARCH_API_KEY` | Bocha API密钥 | https://open.bochaai.com/ | ✅ 支持 |

**功能**：
- 多模态内容搜索
- 图片和视频检索
- 网页内容抓取

**配置说明**：
- Media Engine 必需
- 支持图文混合搜索
- 需要验证API额度

---

## 7. 配置最佳实践

### 7.1 推荐配置流程

**新用户配置步骤**：

1. **配置数据库**（必须）
   ```python
   # 编辑 config.py
   DB_HOST = "localhost"
   DB_USER = "your_user"
   DB_PASSWORD = "your_password"
   DB_NAME = "weiyu_db"
   ```

2. **启动系统**
   ```bash
   python app.py
   ```

3. **访问网页配置界面**
   - 打开浏览器访问 `http://localhost:5000`
   - 点击右上角"⚙️ 配置"按钮

4. **配置各引擎API**
   - 系统已自动填充推荐的 Base URL 和 Model Name
   - 只需填写各服务的 API Key
   - 填写搜索工具的 API Key

5. **保存配置**
   - 点击"保存配置"按钮
   - 配置立即生效

6. **开始使用**
   - 返回主页面
   - 输入查询内容开始分析

### 7.2 安全建议

1. **敏感信息保护**
   - ✅ API Key 通过网页配置保存在浏览器本地
   - ✅ 数据库密码在 config.py 中，不要提交到公开仓库
   - ✅ 使用 `.gitignore` 忽略 config.py
   - ✅ 生产环境使用环境变量

2. **配置备份**
   ```bash
   # 备份网页配置（在浏览器控制台执行）
   localStorage.getItem('weiyu_llm_config')
   
   # 备份文件配置
   cp config.py config.py.backup
   ```

3. **权限控制**
   ```bash
   # 限制配置文件权限
   chmod 600 config.py
   ```

### 7.3 多环境配置

**开发环境**：
```bash
# 使用开发配置
export INSIGHT_ENGINE_API_KEY="dev_key"
export DB_NAME="weiyu_dev"
python app.py
```

**生产环境**：
```bash
# 使用生产配置
export INSIGHT_ENGINE_API_KEY="prod_key"
export DB_NAME="weiyu_prod"
python app.py
```

**Docker部署**：
```yaml
# docker-compose.yml
services:
  weiyu:
    environment:
      - DB_HOST=mysql
      - DB_USER=weiyu
      - DB_PASSWORD=${MYSQL_PASSWORD}
      - INSIGHT_ENGINE_API_KEY=${INSIGHT_KEY}
```

### 7.4 配置验证

**检查配置是否正确**：

```python
# 在 Python 控制台执行
import os
from config import *

# 检查数据库配置
print(f"数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")
print(f"用户: {DB_USER}")

# 检查API配置
print(f"Insight Engine: {INSIGHT_ENGINE_BASE_URL}")
print(f"API Key 已配置: {bool(INSIGHT_ENGINE_API_KEY)}")
```

### 7.5 性能优化建议

1. **模型选择**
   - 快速响应场景：使用小参数模型（7B-30B）
   - 深度分析场景：使用大参数模型（70B-235B）
   - 预算有限：优先使用DeepSeek（性价比高）

2. **并发控制**
   - 各引擎API调用有并发限制
   - 合理设置超时时间
   - 使用重试机制（系统已内置）

3. **缓存策略**
   - 数据库查询结果可缓存
   - 相同查询避免重复调用API
   - 定期清理过期缓存

---

## 8. 常见问题

### Q1: 修改配置后是否需要重启？

**A**: 不需要！

- **网页配置**：保存后立即生效
- **文件配置**：需要重启系统
- **环境变量**：需要重启系统

推荐使用网页配置，可以热更新。

### Q2: 如何切换不同的LLM服务商？

**A**: 在网页配置界面修改相应引擎的 Base URL 和 Model Name。

例如切换 Insight Engine 到 DeepSeek：
- Base URL: `https://api.deepseek.com`
- Model Name: `deepseek-chat`
- API Key: 你的 DeepSeek API Key

### Q3: 配置丢失了怎么办？

**A**: 
- **网页配置**：保存在浏览器 localStorage，除非清除浏览器数据否则不会丢失
- **查看配置**：打开配置界面即可看到当前配置
- **恢复默认**：点击"恢复推荐配置"按钮

### Q4: 数据库如何配置？

**A**: 数据库配置必须在 `config.py` 文件中配置，不支持网页配置。

1. 编辑 `config.py`
2. 修改 `DB_*` 配置项
3. 重启系统

### Q5: 如何验证配置是否正确？

**A**: 
1. 查看启动日志是否有错误
2. 在网页点击"开始"按钮测试
3. 查看控制台输出是否有API调用错误
4. 检查各引擎的状态指示器（右上角圆点）

### Q6: MindSpider 配置在哪里？

**A**: MindSpider 已统一使用主配置文件：
- 数据库配置：自动使用 `config.py` 中的 `DB_*` 配置
- API配置：自动使用 Query Engine 的 DeepSeek 配置
- 无需单独配置 `MindSpider/config.py`

### Q7: 能否使用本地LLM？

**A**: 可以，只要兼容 OpenAI API 格式：

1. 部署本地LLM服务（如 Ollama、LM Studio）
2. 在配置中设置 Base URL 为本地地址
3. 例如：`http://localhost:11434/v1`

### Q8: 多个浏览器的配置是否共享？

**A**: 不共享。每个浏览器的配置独立保存在各自的 localStorage 中。

### Q9: 如何导出配置？

**A**: 目前版本暂不支持配置导出，计划在未来版本添加此功能。

临时方案：
```javascript
// 在浏览器控制台执行
console.log(localStorage.getItem('weiyu_llm_config'));
// 复制输出的JSON字符串保存
```

### Q10: 配置文件和网页配置冲突怎么办？

**A**: 网页配置优先级最高，会覆盖文件配置。

如果不确定，可以：
1. 清除浏览器 localStorage
2. 重新在网页配置

---

## 9. 配置示例

### 9.1 完整配置示例

```python
# config.py - 完整配置示例

import os

# ========== 数据库配置 ==========
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "weiyu_user"
DB_PASSWORD = "SecurePassword123"
DB_NAME = "weiyu_production"
DB_CHARSET = "utf8mb4"

# ========== Insight Engine ==========
INSIGHT_ENGINE_API_KEY = os.getenv("INSIGHT_ENGINE_API_KEY", "")
INSIGHT_ENGINE_BASE_URL = "https://api.moonshot.cn/v1"
INSIGHT_ENGINE_MODEL_NAME = "kimi-k2-0711-preview"

# ========== Media Engine ==========
MEDIA_ENGINE_API_KEY = os.getenv("MEDIA_ENGINE_API_KEY", "")
MEDIA_ENGINE_BASE_URL = "https://www.chataiapi.com/v1"
MEDIA_ENGINE_MODEL_NAME = "gemini-2.5-pro"

# ========== Query Engine ==========
QUERY_ENGINE_API_KEY = os.getenv("QUERY_ENGINE_API_KEY", "")
QUERY_ENGINE_BASE_URL = "https://api.deepseek.com"
QUERY_ENGINE_MODEL_NAME = "deepseek-reasoner"

# ========== Report Engine ==========
REPORT_ENGINE_API_KEY = os.getenv("REPORT_ENGINE_API_KEY", "")
REPORT_ENGINE_BASE_URL = "https://www.chataiapi.com/v1"
REPORT_ENGINE_MODEL_NAME = "gemini-2.5-pro"

# ========== Forum Host ==========
FORUM_HOST_API_KEY = os.getenv("FORUM_HOST_API_KEY", "")
FORUM_HOST_BASE_URL = "https://api.siliconflow.cn/v1"
FORUM_HOST_MODEL_NAME = "Qwen/Qwen3-235B-A22B-Instruct-2507"

# ========== Keyword Optimizer ==========
KEYWORD_OPTIMIZER_API_KEY = os.getenv("KEYWORD_OPTIMIZER_API_KEY", "")
KEYWORD_OPTIMIZER_BASE_URL = "https://api.siliconflow.cn/v1"
KEYWORD_OPTIMIZER_MODEL_NAME = "Qwen/Qwen3-30B-A3B-Instruct-2507"

# ========== 搜索工具 ==========
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
BOCHA_WEB_SEARCH_API_KEY = os.getenv("BOCHA_WEB_SEARCH_API_KEY", "")
```

### 9.2 网页配置JSON示例

```json
{
  "engines": {
    "insight": {
      "api_key": "sk-xxx",
      "base_url": "https://api.moonshot.cn/v1",
      "model_name": "kimi-k2-0711-preview"
    },
    "media": {
      "api_key": "sk-yyy",
      "base_url": "https://www.chataiapi.com/v1",
      "model_name": "gemini-2.5-pro"
    },
    "query": {
      "api_key": "sk-zzz",
      "base_url": "https://api.deepseek.com",
      "model_name": "deepseek-reasoner"
    },
    "report": {
      "api_key": "sk-aaa",
      "base_url": "https://www.chataiapi.com/v1",
      "model_name": "gemini-2.5-pro"
    },
    "forum": {
      "api_key": "sk-bbb",
      "base_url": "https://api.siliconflow.cn/v1",
      "model_name": "Qwen/Qwen3-235B-A22B-Instruct-2507"
    },
    "keyword_optimizer": {
      "api_key": "sk-ccc",
      "base_url": "https://api.siliconflow.cn/v1",
      "model_name": "Qwen/Qwen3-30B-A3B-Instruct-2507"
    }
  },
  "search_tools": {
    "tavily_api_key": "tvly-xxx",
    "bocha_api_key": "sk-ddd"
  }
}
```

---

## 10. 附录

### 10.1 配置文件位置速查

```
配置文件位置                                     用途                      是否需要手动配置
─────────────────────────────────────────────────────────────────────────
/config.py                                      主配置文件                 ✅ 数据库配置必须
MindSpider/config.py                           MindSpider配置（统一）     ❌ 自动从主配置导入
InsightEngine/utils/config.py                  配置加载器                 ❌ 自动读取
MediaEngine/utils/config.py                    配置加载器                 ❌ 自动读取
QueryEngine/utils/config.py                    配置加载器                 ❌ 自动读取
ReportEngine/utils/config.py                   配置加载器                 ❌ 自动读取
浏览器 localStorage                             网页配置存储               ✅ 推荐通过界面配置
```

### 10.2 API服务商速查

| 引擎/工具 | 推荐服务商 | 申请地址 | 特点 |
|-----------|-----------|---------|------|
| Insight Engine | Moonshot Kimi | https://platform.moonshot.cn/ | 超长上下文 |
| Media Engine | Google Gemini | https://www.chataiapi.com/ | 多模态支持 |
| Query Engine | DeepSeek | https://www.deepseek.com/ | 强推理能力 |
| Report Engine | Google Gemini | https://www.chataiapi.com/ | 综合能力强 |
| Forum Host | 硅基流动 Qwen | https://cloud.siliconflow.cn/ | 大参数模型 |
| Keyword Optimizer | 硅基流动 Qwen | https://cloud.siliconflow.cn/ | 快速响应 |
| Tavily Search | Tavily | https://www.tavily.com/ | 实时搜索 |
| Bocha Search | Bocha | https://open.bochaai.com/ | 多模态搜索 |

### 10.3 端口使用情况

| 服务 | 端口 | 说明 |
|------|------|------|
| Flask 主应用 | 5000 | Web界面和API |
| Insight Engine | 8501 | Streamlit UI |
| Media Engine | 8502 | Streamlit UI |
| Query Engine | 8503 | Streamlit UI |
| MySQL 数据库 | 3306 | 数据存储 |

### 10.4 系统要求

- **Python**: 3.8+
- **MySQL**: 5.7+ 或 8.0+
- **内存**: 建议 8GB+
- **磁盘**: 建议 20GB+（存储爬虫数据）
- **浏览器**: Chrome/Firefox/Edge 最新版

---

## 📞 获取帮助

如果您在配置过程中遇到问题：

1. 查看本文档的"常见问题"部分
2. 查看 `WEB_CONFIG_GUIDE.md` - 网页配置详细指南
3. 查看 `README.md` - 项目总体说明
4. 提交 Issue 或联系技术支持

---

**文档版本**: v1.0.0  
**最后更新**: 2025年  
**维护者**: 微舆开发团队
