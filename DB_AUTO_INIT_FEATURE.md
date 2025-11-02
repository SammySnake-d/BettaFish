# 数据库自动初始化功能

## 功能概述

本系统现已支持数据库自动检查和初始化功能。当程序启动时，会自动检查数据库是否存在以及表结构是否完整，如果不存在则会自动创建数据库和表结构，无需手动运行 `python schema/init_database.py` 脚本。

## 实现方式

### 1. 核心模块

创建了 `MindSpider/schema/auto_init_db.py` 模块，提供以下功能：

- 自动检查数据库服务器连接
- 自动检查目标数据库是否存在，不存在则创建
- 自动检查必需的表是否存在，不存在则执行初始化脚本
- 线程安全的单例模式，避免重复初始化
- 支持静默模式，不输出日志信息

### 2. 自动初始化集成

在以下数据库连接类中集成了自动初始化功能：

- `InsightEngine/tools/search.py` - MediaCrawlerDB 类
- `MindSpider/BroadTopicExtraction/database_manager.py` - DatabaseManager 类
- `MindSpider/DeepSentimentCrawling/keyword_manager.py` - KeywordManager 类
- `MindSpider/schema/db_manager.py` - DatabaseManager 类

当这些类初始化时，会自动调用 `_auto_init_database()` 方法检查并初始化数据库。

### 3. 初始化流程

```
1. 检查数据库配置是否完整
2. 连接到 MySQL 服务器（不指定数据库）
3. 检查目标数据库是否存在
   - 不存在：创建数据库
   - 存在：继续
4. 选择目标数据库
5. 检查必需的表（daily_news, daily_topics）是否存在
   - 表不完整：执行 SQL 初始化脚本
     - 执行 MediaCrawler 基础表结构
     - 执行 MindSpider 扩展表结构
   - 表完整：跳过初始化
6. 完成初始化
```

## 使用说明

### 自动模式（推荐）

现在，您只需要配置好 `config.py` 中的数据库连接信息：

```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "your_db_name"
DB_CHARSET = "utf8mb4"
```

然后直接启动应用即可：

```bash
# 启动主应用
python app.py

# 或启动单独的 Engine
streamlit run SingleEngineApp/insight_engine_streamlit_app.py

# 或运行 MindSpider 爬虫
cd MindSpider
python main.py --setup
```

系统会自动检查并初始化数据库，无需手动操作。

### 手动模式

如果您仍希望手动初始化数据库，可以运行：

```bash
cd MindSpider
python schema/init_database.py
```

或者单独测试自动初始化功能：

```bash
cd MindSpider
python schema/auto_init_db.py
```

## 错误处理

如果自动初始化失败，系统会：

1. 打印警告信息，说明初始化失败的原因
2. 提示用户手动运行初始化脚本
3. 继续尝试连接数据库（如果数据库已存在）

这样既保证了自动化，又不会因为初始化失败而中断程序。

## 注意事项

1. **数据库权限**：确保配置的数据库用户具有创建数据库和表的权限
2. **网络连接**：确保能够连接到 MySQL 服务器
3. **表结构文件**：自动初始化依赖以下 SQL 文件：
   - `MindSpider/DeepSentimentCrawling/MediaCrawler/schema/tables.sql`
   - `MindSpider/schema/mindspider_tables.sql`

## 技术细节

### 线程安全

使用全局锁和状态标志确保多线程环境下只初始化一次：

```python
_init_lock = threading.Lock()
_init_status = {'initialized': False, 'error': None}
```

### 静默模式

为了避免在日志中产生过多输出，支持静默模式：

```python
check_and_init_database(config, silent=True)
```

### 兼容性

自动初始化功能向后兼容，不影响现有的手动初始化流程。

## 常见问题

### Q: 如何确认数据库已经自动初始化？

A: 查看程序启动日志，会显示以下信息之一：
- "数据库 'xxx' 已存在"
- "数据库 'xxx' 不存在，正在创建..."
- "数据库表结构完整，无需初始化"
- "正在初始化数据库表结构..."

### Q: 自动初始化失败怎么办？

A: 系统会打印警告信息并给出手动初始化的提示。您可以：
1. 检查数据库配置是否正确
2. 检查数据库用户权限
3. 手动运行 `python schema/init_database.py`

### Q: 会不会重复初始化？

A: 不会。系统使用单例模式和状态检查，确保只初始化一次。

### Q: 自动初始化会影响性能吗？

A: 初始化检查非常快速（通常不到1秒），只在程序启动时执行一次，不会影响运行时性能。

## 更新历史

- 2025-01-XX: 添加数据库自动初始化功能
  - 创建 auto_init_db.py 模块
  - 在所有数据库连接类中集成自动初始化
  - 添加线程安全和错误处理机制
