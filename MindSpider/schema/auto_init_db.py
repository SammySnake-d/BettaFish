#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库自动初始化模块
用于在程序启动时自动检查并初始化数据库
"""

import os
import sys
import pymysql
from pathlib import Path
import threading

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 全局锁，防止多线程同时初始化
_init_lock = threading.Lock()
_init_status = {'initialized': False, 'error': None}


def check_and_init_database(config_module, silent=False):
    """
    检查数据库是否存在，如果不存在则自动初始化
    
    Args:
        config_module: 配置模块（例如 import config 后的 config 对象）
        silent: 是否静默模式（不打印信息）
    
    Returns:
        bool: 初始化是否成功
    """
    with _init_lock:
        # 如果已经初始化过，直接返回结果
        if _init_status['initialized']:
            return True
        if _init_status['error']:
            if not silent:
                print(f"数据库初始化曾失败: {_init_status['error']}")
            return False
        
        try:
            config = config_module
            
            # 第一步：尝试连接到数据库（不指定具体数据库名）
            if not silent:
                print(f"检查数据库连接: {config.DB_HOST}:{config.DB_PORT}")
            
            connection = None
            try:
                connection = pymysql.connect(
                    host=config.DB_HOST,
                    port=config.DB_PORT,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    charset=config.DB_CHARSET,
                    autocommit=True
                )
            except Exception as e:
                error_msg = f"无法连接到MySQL服务器: {e}"
                _init_status['error'] = error_msg
                if not silent:
                    print(error_msg)
                return False
            
            cursor = connection.cursor()
            
            # 第二步：检查数据库是否存在
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            
            if config.DB_NAME not in databases:
                if not silent:
                    print(f"数据库 '{config.DB_NAME}' 不存在，正在创建...")
                # 创建数据库
                cursor.execute(f"CREATE DATABASE `{config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                if not silent:
                    print(f"数据库 '{config.DB_NAME}' 创建成功")
            else:
                if not silent:
                    print(f"数据库 '{config.DB_NAME}' 已存在")
            
            # 第三步：选择数据库并检查表
            cursor.execute(f"USE `{config.DB_NAME}`")
            cursor.execute("SHOW TABLES")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            # 检查必需的表是否存在
            required_tables = ['daily_news', 'daily_topics']
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                if not silent:
                    print(f"缺少必需的表: {', '.join(missing_tables)}")
                    print("正在初始化数据库表结构...")
                
                # 第四步：执行表结构初始化
                schema_dir = Path(__file__).parent
                
                # 1. 执行MediaCrawler的原始表结构
                mediacrawler_sql = schema_dir.parent / "DeepSentimentCrawling" / "MediaCrawler" / "schema" / "tables.sql"
                if mediacrawler_sql.exists():
                    if not silent:
                        print("创建MediaCrawler基础表...")
                    _execute_sql_file(connection, str(mediacrawler_sql), silent)
                else:
                    if not silent:
                        print("警告: MediaCrawler SQL文件不存在，跳过基础表创建")
                
                # 2. 执行MindSpider扩展表结构
                mindspider_sql = schema_dir / "mindspider_tables.sql"
                if mindspider_sql.exists():
                    if not silent:
                        print("创建MindSpider扩展表...")
                    _execute_sql_file(connection, str(mindspider_sql), silent)
                else:
                    error_msg = "错误: MindSpider SQL文件不存在"
                    _init_status['error'] = error_msg
                    if not silent:
                        print(error_msg)
                    connection.close()
                    return False
                
                if not silent:
                    print("数据库表结构初始化完成")
            else:
                if not silent:
                    print("数据库表结构完整，无需初始化")
            
            connection.close()
            _init_status['initialized'] = True
            if not silent:
                print("数据库检查完成，可以正常使用")
            return True
            
        except Exception as e:
            error_msg = f"数据库初始化失败: {e}"
            _init_status['error'] = error_msg
            if not silent:
                print(error_msg)
            return False


def _execute_sql_file(connection, sql_file_path, silent=False):
    """执行SQL文件"""
    try:
        cursor = connection.cursor()
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（按分号分割）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        success_count = 0
        error_count = 0
        
        for stmt in sql_statements:
            if not stmt or stmt.startswith('--'):
                continue
            try:
                cursor.execute(stmt)
                success_count += 1
            except Exception as e:
                error_count += 1
                if not silent:
                    print(f"执行SQL语句失败: {str(e)[:100]}...")
        
        if not silent:
            print(f"成功执行: {success_count} 条语句, 失败: {error_count} 条语句")
        
        return error_count == 0
    
    except Exception as e:
        if not silent:
            print(f"执行SQL文件失败 {sql_file_path}: {e}")
        return False


def reset_init_status():
    """重置初始化状态（用于测试）"""
    global _init_status
    with _init_lock:
        _init_status = {'initialized': False, 'error': None}


if __name__ == "__main__":
    # 测试代码
    try:
        import config
        success = check_and_init_database(config, silent=False)
        if success:
            print("\n✓ 数据库自动初始化测试成功")
        else:
            print("\n✗ 数据库自动初始化测试失败")
            sys.exit(1)
    except ImportError:
        print("错误: 无法导入config.py配置文件")
        sys.exit(1)
