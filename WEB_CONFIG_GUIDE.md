# 网页配置使用指南

## 🎉 新功能：网页可视化配置

现在您可以通过网页界面轻松配置所有的 LLM 和 API 密钥，无需手动编辑配置文件！

## 📝 使用方法

### 1. 打开配置界面

在微舆主页面，点击右上角的 **⚙️ 配置** 按钮，即可打开配置界面。

### 2. 配置各个引擎

配置界面提供了以下引擎的配置选项：

- **Insight Engine** - 私有数据库挖掘
- **Media Engine** - 多模态内容分析
- **Query Engine** - 精准信息搜索
- **Report Engine** - 最终报告生成
- **Forum Host** - 多智能体主持人
- **Keyword Optimizer** - SQL 关键词优化

每个引擎需要配置以下三项：

- **Base URL**: LLM 服务的 API 地址
- **Model Name**: 使用的模型名称
- **API Key**: 您的 API 密钥

### 3. 配置搜索工具

除了引擎配置，还可以配置以下搜索工具：

- **Tavily API Key**: 用于 Query Agent 的联网检索
- **Bocha Web Search API Key**: 用于 Media Agent 的网页搜索

### 4. 保存配置

填写完毕后，点击 **保存配置** 按钮。配置将：

1. 保存到浏览器的 localStorage 中
2. 自动应用到运行中的系统
3. 下次打开页面时自动加载

### 5. 恢复推荐配置

如果需要恢复到推荐的默认配置，点击 **恢复推荐配置** 按钮。注意：这不会清除您已输入的 API Key。

## 🔒 安全性

- 所有配置保存在**浏览器本地存储**中，不会上传到服务器
- API Key 使用密码框输入，不会明文显示
- 配置数据仅在本地浏览器中存储，确保安全

## 📋 推荐配置

系统提供了以下推荐配置：

| 引擎 | 推荐服务 | 申请地址 |
|-----|---------|---------|
| Insight Engine | Kimi (Moonshot) | https://platform.moonshot.cn/ |
| Media Engine | Gemini | https://www.chataiapi.com/ |
| Query Engine | DeepSeek | https://www.deepseek.com/ |
| Report Engine | Gemini | https://www.chataiapi.com/ |
| Forum Host | Qwen (硅基流动) | https://cloud.siliconflow.cn/ |
| Keyword Optimizer | Qwen (硅基流动) | https://cloud.siliconflow.cn/ |
| Tavily Search | Tavily | https://www.tavily.com/ |
| Bocha Search | Bocha | https://open.bochaai.com/ |

## 🔧 配置文件（备用）

如果您需要使用配置文件，仍然可以编辑 `config.py`：

- **数据库配置**：必须在 `config.py` 中配置
- **LLM 配置**：可以在 `config.py` 中设置默认值，但网页配置优先级更高

## 💡 使用提示

1. **首次使用**：打开配置界面，系统会自动填充推荐的 Base URL 和 Model Name，您只需填写 API Key
2. **切换配置**：您可以随时修改配置，保存后立即生效
3. **多浏览器**：不同浏览器的配置是独立的，您可以在不同浏览器中使用不同的配置
4. **清除配置**：如需清除配置，可以清除浏览器的 localStorage 或重新输入新的配置

## 🆘 常见问题

**Q: 配置保存后何时生效？**  
A: 保存后立即生效，新的 API 调用会使用新的配置。

**Q: 如何查看当前使用的配置？**  
A: 点击配置按钮，界面会自动加载当前保存的配置。

**Q: 配置丢失了怎么办？**  
A: 配置保存在浏览器 localStorage 中，除非手动清除浏览器数据，否则不会丢失。

**Q: 可以导出/导入配置吗？**  
A: 当前版本暂不支持，未来版本会添加此功能。

**Q: 数据库配置在哪里？**  
A: 数据库配置仅支持在 `config.py` 文件中配置，不支持网页配置。

## 🎯 优势

使用网页配置的优势：

✅ **简单易用**：可视化界面，无需编辑代码  
✅ **即时生效**：保存后立即应用，无需重启  
✅ **持久保存**：浏览器本地存储，刷新页面自动加载  
✅ **安全可靠**：数据存储在本地，不会泄露  
✅ **灵活切换**：可随时修改，支持多种 LLM 服务  

享受更便捷的配置体验！🎉
