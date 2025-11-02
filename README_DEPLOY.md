# 🚀 微舆 (BettaFish) 一键部署

## 快速部署

### Windows

```batch
# 1. 下载项目
git clone https://github.com/SammySnake-d/BettaFish.git
cd BettaFish

# 2. 运行部署脚本
deploy.bat

# 3. 启动应用
start.bat
```

### Linux/macOS

```bash
# 1. 下载项目
git clone https://github.com/SammySnake-d/BettaFish.git
cd BettaFish

# 2. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 3. 启动应用
./start.sh
```

## 配置流程

### 1. 打开浏览器

访问: http://localhost:5000

### 2. 点击配置按钮

点击右上角的 **⚙️ 配置** 按钮

### 3. 配置各项参数

#### 必需配置（最小配置）

**Query Engine**（DeepSeek）
- Base URL: `https://api.deepseek.com`
- Model Name: `deepseek-reasoner`
- API Key: `your_deepseek_key`

**Tavily 搜索**
- API Key: `your_tavily_key`

#### 推荐配置（完整功能）

**所有 6 个引擎 + 2 个搜索工具**

详见配置指南：`DEPLOY_GUIDE.md`

#### 可选配置

**数据库配置**（仅在使用 Insight Engine 或 MindSpider 时需要）
- 主机: `localhost`
- 端口: `3306`
- 用户名: `your_username`
- 密码: `your_password`
- 数据库名: `weiyu_db`
- 字符集: `utf8mb4`

**WebDAV 备份**（推荐）
- 服务器地址: `https://dav.jianguoyun.com/dav/`
- 用户名: `your_email`
- 密码: `your_app_password`

### 4. 保存配置

点击 **保存配置** 按钮

### 5. 开始使用

所有配置会自动保存在浏览器本地！

## 特点

✅ **零配置文件** - 所有配置通过网页界面完成  
✅ **本地存储** - 配置保存在浏览器 localStorage  
✅ **云备份** - 支持 WebDAV 云备份和恢复  
✅ **热更新** - 配置修改后立即生效，无需重启  
✅ **导入导出** - 支持配置文件导入导出  
✅ **多浏览器** - 可在不同浏览器/设备间同步配置  

## 配置优先级

```
网页配置（localStorage） > 环境变量 > config.py 默认值
```

## 目录结构

```
BettaFish/
├── deploy.sh / deploy.bat    # 一键部署脚本
├── start.sh / start.bat       # 快速启动脚本
├── app.py                     # 主应用程序
├── config.py                  # 配置文件（可选，推荐使用网页配置）
├── requirements.txt           # Python 依赖
└── DEPLOY_GUIDE.md           # 详细部署指南
```

## 配置管理

### 导出配置

点击 **💾 导出到本地** 按钮，保存为 JSON 文件

### 导入配置

点击 **📂 从本地导入** 按钮，选择 JSON 文件

### WebDAV 备份

点击 **☁️ 备份到WebDAV** 按钮，自动备份到云端

### WebDAV 恢复

点击 **☁️ 从WebDAV恢复** 按钮，从云端恢复最新配置

### 重置配置

点击 **恢复推荐配置** 按钮，恢复所有参数到推荐值

## 故障排除

### Python 未找到

**Windows**: 安装 Python 3.8+ 并勾选 "Add Python to PATH"  
**Linux/macOS**: `sudo apt-get install python3` 或 `brew install python3`

### 端口被占用

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### 数据库连接失败

1. 确保 MySQL 服务正在运行
2. 检查用户名密码是否正确
3. 确认数据库已创建

```sql
CREATE DATABASE weiyu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 文档

- `DEPLOY_GUIDE.md` - 详细部署指南
- `CONFIGURATION_GUIDE.md` - 完整配置指南
- `ADVANCED_CONFIG_GUIDE.md` - 高级配置说明
- `STARTUP_GUIDE.md` - 启动问题解决
- `WEB_CONFIG_GUIDE.md` - 网页配置详解

## API 密钥申请

| 服务 | 申请地址 | 用途 |
|------|----------|------|
| Kimi | https://platform.moonshot.cn/ | Insight Engine |
| DeepSeek | https://www.deepseek.com/ | Query Engine |
| Gemini | https://ai.google.dev/ | Media/Report Engine |
| Qwen | https://cloud.siliconflow.cn/ | Forum Host |
| Tavily | https://www.tavily.com/ | 联网搜索 |
| Bocha | https://open.bochaai.com/ | 网页搜索 |

## 获取帮助

- GitHub Issues: 提交问题和建议
- 项目文档: 查看完整文档
- QQ 群: 670939375（云数据库申请）

## License

MIT License

---

**版本**: v2.0  
**最后更新**: 2025-01-10  
**开发团队**: 微舆开发团队
