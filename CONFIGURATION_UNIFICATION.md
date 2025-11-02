# 配置系统统一化说明

## 📋 概述

本次更新统一了微舆系统的配置管理，解决了配置分散和重复的问题。

## 🔄 主要变更

### 1. 配置统一

**之前**：
- 主配置：`/config.py`
- MindSpider配置：`/MindSpider/config.py`（独立配置）
- 两处配置需要分别维护，容易不一致

**现在**：
- 主配置：`/config.py`（唯一配置来源）
- MindSpider配置：`/MindSpider/config.py`（自动从主配置导入）
- 一处配置，全局生效

### 2. 配置方式增强

提供三种配置方式，优先级从高到低：

```
1. 网页配置（最高优先级）
   ↓ 覆盖
2. 环境变量
   ↓ 覆盖
3. 配置文件（默认值）
```

### 3. MindSpider配置整合

**MindSpider/config.py 现在的逻辑**：

```python
# 1. 尝试从主配置导入数据库配置
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET

# 2. DeepSeek API自动配置
# 优先使用环境变量 DEEPSEEK_API_KEY
# 如果未设置，自动使用 Query Engine 的配置（如果它使用DeepSeek）
```

**优势**：
- ✅ 无需重复配置数据库信息
- ✅ 自动共享LLM API配置
- ✅ 保持向后兼容
- ✅ 支持独立运行（环境变量备用方案）

## 📊 配置文件对应关系

| 文件 | 作用 | 是否需要手动配置 |
|------|------|-----------------|
| `/config.py` | 主配置文件 | ✅ 数据库必须配置 |
| `/MindSpider/config.py` | MindSpider配置 | ❌ 自动从主配置导入 |
| `/InsightEngine/utils/config.py` | InsightEngine配置加载器 | ❌ 自动读取主配置 |
| `/MediaEngine/utils/config.py` | MediaEngine配置加载器 | ❌ 自动读取主配置 |
| `/QueryEngine/utils/config.py` | QueryEngine配置加载器 | ❌ 自动读取主配置 |
| `/ReportEngine/utils/config.py` | ReportEngine配置加载器 | ❌ 自动读取主配置 |

## 🎯 运行模式确认

### 微舆是运行时服务 ✅

系统采用**运行时服务模式**，启动后持续运行，不是单次启动结束。

**证据**：

```python
# app.py
if __name__ == '__main__':
    # ... 启动各个子服务 ...
    
    # Flask应用持续运行
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    # 这会阻塞，直到手动停止（Ctrl+C）
```

**运行的服务组件**：

1. **Flask Web服务器** - 端口 5000
   - 提供Web界面
   - 提供REST API
   - 提供WebSocket连接

2. **Streamlit子应用**（3个）
   - Insight Engine UI - 端口 8501
   - Media Engine UI - 端口 8502
   - Query Engine UI - 端口 8503

3. **ForumEngine监控器**（后台线程）
   - 持续监控日志文件
   - 生成主持人发言
   - 写入forum.log

4. **ReportEngine**（待命状态）
   - 监听生成请求
   - 异步生成报告
   - 返回结果

**停止方式**：
- Ctrl+C 发送中断信号
- 系统执行清理后退出

## 🔧 配置使用指南

### 新用户快速配置

#### 步骤1: 配置数据库（必须）

编辑 `/config.py`：

```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "weiyu_user"
DB_PASSWORD = "your_secure_password"
DB_NAME = "weiyu_db"
```

#### 步骤2: 启动系统

```bash
cd /home/engine/project
python app.py
```

系统会输出启动信息，等待所有服务启动完成。

#### 步骤3: 网页配置LLM

1. 浏览器访问：`http://localhost:5000`
2. 点击右上角 **⚙️ 配置** 按钮
3. 填写各引擎的API Key
4. 点击 **保存配置**

#### 步骤4: 开始使用

返回主页面，输入查询内容，点击"开始"按钮。

### 已有用户迁移

如果你之前在 `MindSpider/config.py` 中配置了数据库：

1. **复制数据库配置到主配置文件**：
   ```bash
   # 备份MindSpider配置
   cp MindSpider/config.py MindSpider/config.py.old
   
   # 将数据库配置复制到主配置文件
   # 编辑 /config.py，填入数据库信息
   ```

2. **MindSpider配置会自动读取主配置**：
   - 新的 `MindSpider/config.py` 会自动导入主配置
   - 无需手动维护

3. **DeepSeek API自动配置**：
   - 通过网页配置 Query Engine 使用 DeepSeek
   - MindSpider 会自动使用该配置

## 📚 配置文档

我们提供了详细的配置文档：

1. **CONFIGURATION_GUIDE.md** - 完整配置指南（新建）
   - 所有配置项的详细说明
   - 各引擎配置详解
   - 配置最佳实践
   - 常见问题解答

2. **WEB_CONFIG_GUIDE.md** - 网页配置使用指南
   - 网页配置步骤
   - 推荐配置
   - 安全性说明

3. **WEB_CONFIG_CHANGELOG.md** - 更新日志
   - 功能变更记录
   - 技术实现说明

## 🔍 配置验证

### 验证数据库配置

```bash
cd /home/engine/project
python3 << EOF
from config import DB_HOST, DB_PORT, DB_USER, DB_NAME
print(f"数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")
print(f"用户: {DB_USER}")
EOF
```

### 验证MindSpider配置

```bash
cd /home/engine/project/MindSpider
python3 << EOF
import config
print(f"数据库: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
print(f"DeepSeek API: {'已配置' if config.DEEPSEEK_API_KEY else '未配置'}")
EOF
```

### 验证配置导入

```bash
cd /home/engine/project
python3 << EOF
# 测试从主配置导入
from config import *
print("主配置导入成功")

# 测试MindSpider配置导入
import sys
sys.path.insert(0, 'MindSpider')
import config as ms_config
print("MindSpider配置导入成功")
print(f"数据库配置一致: {ms_config.DB_HOST == DB_HOST}")
EOF
```

## ⚠️ 注意事项

### 1. 数据库配置

- ❌ 不支持网页配置（安全考虑）
- ✅ 必须在 `config.py` 或环境变量中配置
- ✅ 修改后需要重启系统

### 2. LLM API配置

- ✅ 推荐使用网页配置（热更新）
- ✅ 也可以使用环境变量（容器化部署）
- ✅ 配置文件作为默认值

### 3. 配置优先级

记住优先级顺序：**网页配置 > 环境变量 > 配置文件**

### 4. MindSpider配置

- ❌ 不要手动编辑 `MindSpider/config.py`
- ✅ 所有配置通过主配置文件
- ✅ 系统会自动同步

### 5. 配置保存

- 网页配置：保存在浏览器 localStorage
- 文件配置：保存在磁盘
- 环境变量：仅存在于当前会话

## 🚀 升级优势

### 之前的问题

1. ❌ 配置分散在多个文件
2. ❌ 需要重复配置数据库信息
3. ❌ MindSpider配置容易被忽略
4. ❌ 配置不一致导致错误
5. ❌ 难以统一管理

### 现在的优势

1. ✅ 配置统一在主配置文件
2. ✅ 自动共享数据库配置
3. ✅ MindSpider自动使用主配置
4. ✅ 配置一致性保证
5. ✅ 网页可视化配置
6. ✅ 热更新无需重启
7. ✅ 配置持久化保存
8. ✅ 多种配置方式灵活选择

## 📝 总结

### 关键变更

1. **配置统一化**：所有配置统一到主配置文件
2. **自动导入**：MindSpider自动从主配置导入
3. **运行时服务**：系统持续运行，提供服务
4. **网页配置**：可视化配置界面，热更新
5. **详细文档**：提供完整的配置指南

### 配置流程

```
1. 编辑主配置文件（数据库）
   ↓
2. 启动系统（python app.py）
   ↓
3. 打开网页配置界面
   ↓
4. 配置各引擎API
   ↓
5. 保存配置（立即生效）
   ↓
6. 开始使用
```

### 推荐阅读顺序

1. 本文档（CONFIGURATION_UNIFICATION.md）- 了解变更
2. CONFIGURATION_GUIDE.md - 学习完整配置
3. WEB_CONFIG_GUIDE.md - 掌握网页配置

---

**更新日期**: 2025年  
**版本**: v1.0.0 - 配置统一化版本  
**维护者**: 微舆开发团队
