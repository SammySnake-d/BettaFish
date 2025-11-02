# -*- coding: utf-8 -*-
"""
微舆配置文件
注意：LLM 和 API 密钥配置现在可以通过网页界面进行配置，保存在浏览器本地存储中。
本文件仅用于数据库配置和作为备用配置。
"""

import os

# ============================== 数据库配置 ==============================
# 配置这些值以连接到您的MySQL实例。
# 数据库配置必须在此文件中配置，不支持网页配置。
DB_HOST = os.getenv("DB_HOST", "your_db_host")  # 例如："localhost" 或 "127.0.0.1"
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "your_db_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_db_password")
DB_NAME = os.getenv("DB_NAME", "your_db_name")
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")
# 我们也提供云数据库资源便捷配置，日均10w+数据，可免费申请，联系我们：670939375@qq.com
# NOTE：为进行数据合规性审查与服务升级，云数据库自2025年10月1日起暂停接收新的使用申请


# ============================== LLM配置（推荐通过网页配置） ==============================
# ⚙️ 推荐使用网页配置界面进行配置！
# 点击网页右上角的"⚙️ 配置"按钮，即可在可视化界面中配置所有 LLM 和 API Key。
# 配置会自动保存在浏览器本地，每次打开自动加载，非常方便！
#
# 下面的配置项仅作为备用配置或环境变量未设置时的默认值。
# 您可以更改每个部分LLM使用的API，🚩只要兼容OpenAI请求格式都可以，定义好KEY、BASE_URL与MODEL_NAME即可正常使用。

# Insight Agent（推荐Kimi，申请地址：https://platform.moonshot.cn/）
INSIGHT_ENGINE_API_KEY = os.getenv("INSIGHT_ENGINE_API_KEY", "")
INSIGHT_ENGINE_BASE_URL = os.getenv("INSIGHT_ENGINE_BASE_URL", "https://api.moonshot.cn/v1")
INSIGHT_ENGINE_MODEL_NAME = os.getenv("INSIGHT_ENGINE_MODEL_NAME", "kimi-k2-0711-preview")

# Media Agent（推荐Gemini，这里我用了一个中转厂商，你也可以换成你自己的，申请地址：https://www.chataiapi.com/）
MEDIA_ENGINE_API_KEY = os.getenv("MEDIA_ENGINE_API_KEY", "")
MEDIA_ENGINE_BASE_URL = os.getenv("MEDIA_ENGINE_BASE_URL", "https://www.chataiapi.com/v1")
MEDIA_ENGINE_MODEL_NAME = os.getenv("MEDIA_ENGINE_MODEL_NAME", "gemini-2.5-pro")

# Query Agent（推荐DeepSeek，申请地址：https://www.deepseek.com/）
QUERY_ENGINE_API_KEY = os.getenv("QUERY_ENGINE_API_KEY", "")
QUERY_ENGINE_BASE_URL = os.getenv("QUERY_ENGINE_BASE_URL", "https://api.deepseek.com")
QUERY_ENGINE_MODEL_NAME = os.getenv("QUERY_ENGINE_MODEL_NAME", "deepseek-reasoner")

# Report Agent（推荐Gemini，这里我用了一个中转厂商，你也可以换成你自己的，申请地址：https://www.chataiapi.com/）
REPORT_ENGINE_API_KEY = os.getenv("REPORT_ENGINE_API_KEY", "")
REPORT_ENGINE_BASE_URL = os.getenv("REPORT_ENGINE_BASE_URL", "https://www.chataiapi.com/v1")
REPORT_ENGINE_MODEL_NAME = os.getenv("REPORT_ENGINE_MODEL_NAME", "gemini-2.5-pro")

# Forum Host（Qwen最新模型，这里我使用了硅基流动这个平台，申请地址：https://cloud.siliconflow.cn/）
FORUM_HOST_API_KEY = os.getenv("FORUM_HOST_API_KEY", "")
FORUM_HOST_BASE_URL = os.getenv("FORUM_HOST_BASE_URL", "https://api.siliconflow.cn/v1")
FORUM_HOST_MODEL_NAME = os.getenv("FORUM_HOST_MODEL_NAME", "Qwen/Qwen3-235B-A22B-Instruct-2507")

# SQL keyword Optimizer（小参数Qwen模型，这里我使用了硅基流动这个平台，申请地址：https://cloud.siliconflow.cn/）
KEYWORD_OPTIMIZER_API_KEY = os.getenv("KEYWORD_OPTIMIZER_API_KEY", "")
KEYWORD_OPTIMIZER_BASE_URL = os.getenv("KEYWORD_OPTIMIZER_BASE_URL", "https://api.siliconflow.cn/v1")
KEYWORD_OPTIMIZER_MODEL_NAME = os.getenv("KEYWORD_OPTIMIZER_MODEL_NAME", "Qwen/Qwen3-30B-A3B-Instruct-2507")


# ============================== 网络工具配置（推荐通过网页配置） ==============================
# ⚙️ 推荐使用网页配置界面进行配置！
# Tavily API（申请地址：https://www.tavily.com/）
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Bocha API（申请地址：https://open.bochaai.com/）
BOCHA_WEB_SEARCH_API_KEY = os.getenv("BOCHA_WEB_SEARCH_API_KEY", "")


# ============================== 高级配置（可通过网页配置） ==============================
# ⚙️ 这些高级参数可以通过网页配置界面的"高级配置"部分进行调整

# Query Engine 高级配置
QUERY_MAX_REFLECTIONS = int(os.getenv("QUERY_MAX_REFLECTIONS", 2))  # 反思轮次
QUERY_MAX_SEARCH_RESULTS = int(os.getenv("QUERY_MAX_SEARCH_RESULTS", 20))  # 最大搜索结果数
QUERY_MAX_CONTENT_LENGTH = int(os.getenv("QUERY_MAX_CONTENT_LENGTH", 20000))  # 最大内容长度
QUERY_SEARCH_TIMEOUT = int(os.getenv("QUERY_SEARCH_TIMEOUT", 240))  # 搜索超时（秒）

# Media Engine 高级配置
MEDIA_MAX_REFLECTIONS = int(os.getenv("MEDIA_MAX_REFLECTIONS", 2))  # 反思轮次
MEDIA_MAX_PARAGRAPHS = int(os.getenv("MEDIA_MAX_PARAGRAPHS", 5))  # 最大段落数
MEDIA_MAX_CONTENT_LENGTH = int(os.getenv("MEDIA_MAX_CONTENT_LENGTH", 20000))  # 最大内容长度
MEDIA_SEARCH_TIMEOUT = int(os.getenv("MEDIA_SEARCH_TIMEOUT", 240))  # 搜索超时（秒）

# Insight Engine 高级配置
INSIGHT_MAX_REFLECTIONS = int(os.getenv("INSIGHT_MAX_REFLECTIONS", 3))  # 反思轮次
INSIGHT_MAX_PARAGRAPHS = int(os.getenv("INSIGHT_MAX_PARAGRAPHS", 6))  # 最大段落数
INSIGHT_MAX_CONTENT_LENGTH = int(os.getenv("INSIGHT_MAX_CONTENT_LENGTH", 500000))  # 最大内容长度
INSIGHT_SEARCH_TIMEOUT = int(os.getenv("INSIGHT_SEARCH_TIMEOUT", 240))  # 搜索超时（秒）

# Insight Engine 搜索限制配置
INSIGHT_SEARCH_HOT_CONTENT_LIMIT = int(os.getenv("INSIGHT_SEARCH_HOT_CONTENT_LIMIT", 100))  # 热点内容搜索限制
INSIGHT_SEARCH_TOPIC_GLOBALLY_LIMIT = int(os.getenv("INSIGHT_SEARCH_TOPIC_GLOBALLY_LIMIT", 50))  # 全局话题搜索限制（每表）
INSIGHT_SEARCH_TOPIC_BY_DATE_LIMIT = int(os.getenv("INSIGHT_SEARCH_TOPIC_BY_DATE_LIMIT", 100))  # 按日期话题搜索限制（每表）
INSIGHT_GET_COMMENTS_LIMIT = int(os.getenv("INSIGHT_GET_COMMENTS_LIMIT", 500))  # 评论获取限制
INSIGHT_SEARCH_TOPIC_ON_PLATFORM_LIMIT = int(os.getenv("INSIGHT_SEARCH_TOPIC_ON_PLATFORM_LIMIT", 200))  # 平台话题搜索限制
INSIGHT_MAX_SEARCH_RESULTS_FOR_LLM = int(os.getenv("INSIGHT_MAX_SEARCH_RESULTS_FOR_LLM", 50))  # 传给LLM的最大结果数

# 情感分析配置
SENTIMENT_MODEL_TYPE = os.getenv("SENTIMENT_MODEL_TYPE", "multilingual")  # 模型类型
SENTIMENT_CONFIDENCE_THRESHOLD = float(os.getenv("SENTIMENT_CONFIDENCE_THRESHOLD", 0.8))  # 置信度阈值
SENTIMENT_BATCH_SIZE = int(os.getenv("SENTIMENT_BATCH_SIZE", 32))  # 批处理大小
SENTIMENT_MAX_SEQUENCE_LENGTH = int(os.getenv("SENTIMENT_MAX_SEQUENCE_LENGTH", 512))  # 最大序列长度

# WebDAV 备份配置（可选）
WEBDAV_URL = os.getenv("WEBDAV_URL", "")  # WebDAV服务器URL
WEBDAV_USERNAME = os.getenv("WEBDAV_USERNAME", "")  # WebDAV用户名
WEBDAV_PASSWORD = os.getenv("WEBDAV_PASSWORD", "")  # WebDAV密码