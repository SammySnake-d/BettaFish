# -*- coding: utf-8 -*-
"""
MindSpider配置文件
从外层系统导入数据库配置，保证MindSpider和舆情系统使用同一个数据库
"""

import importlib.util
from pathlib import Path

# 外层系统的配置文件路径
ROOT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.py"

if not ROOT_CONFIG_PATH.exists():
    raise FileNotFoundError(
        "未找到外层系统的配置文件 config.py，请确保项目根目录下存在该文件。"
    )

# 动态导入外层系统配置
spec = importlib.util.spec_from_file_location("outer_config", ROOT_CONFIG_PATH)
outer_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(outer_config)

required_db_fields = (
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
    "DB_CHARSET",
)

missing_fields = [field for field in required_db_fields if not hasattr(outer_config, field)]
if missing_fields:
    raise AttributeError(
        "外层系统的 config.py 缺少以下数据库配置项: " + ", ".join(missing_fields)
    )

# 数据库配置（与外层系统保持一致）
DB_HOST = outer_config.DB_HOST
DB_PORT = outer_config.DB_PORT
DB_USER = outer_config.DB_USER
DB_PASSWORD = outer_config.DB_PASSWORD
DB_NAME = outer_config.DB_NAME
DB_CHARSET = outer_config.DB_CHARSET

# MindSpider特有配置
# DeepSeek API密钥（用于话题提取）
DEEPSEEK_API_KEY = getattr(outer_config, "DEEPSEEK_API_KEY", "your_deepseek_api_key")
