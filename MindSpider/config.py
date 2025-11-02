# -*- coding: utf-8 -*-
"""
MindSpider 配置文件 - 统一使用根目录的配置
注意：此配置文件现在从根目录的 config.py 导入配置，无需单独配置
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 从根目录配置文件导入数据库配置
try:
    from config import (
        DB_HOST,
        DB_PORT,
        DB_USER,
        DB_PASSWORD,
        DB_NAME,
        DB_CHARSET
    )
except ImportError:
    # 如果导入失败，使用默认值
    DB_HOST = os.getenv("DB_HOST", "your_host")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "your_username")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
    DB_NAME = os.getenv("DB_NAME", "mindspider")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# DeepSeek API密钥 - 现在可以通过网页配置或环境变量设置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 如果没有设置，可以尝试从主配置导入
if not DEEPSEEK_API_KEY:
    try:
        from config import QUERY_ENGINE_API_KEY, QUERY_ENGINE_BASE_URL
        # 如果Query Engine使用DeepSeek，则使用其API Key
        if "deepseek" in QUERY_ENGINE_BASE_URL.lower():
            DEEPSEEK_API_KEY = QUERY_ENGINE_API_KEY
    except ImportError:
        pass
