"""
WebDAV备份工具
支持将配置备份到WebDAV服务器，并从WebDAV恢复配置
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
try:
    from webdav3.client import Client
    WEBDAV_AVAILABLE = True
except ImportError:
    WEBDAV_AVAILABLE = False
    print("WebDAV库未安装，备份功能将不可用。安装: pip install webdavclient3")


class WebDAVBackupManager:
    """WebDAV配置备份管理器"""
    
    def __init__(self, webdav_url: str = "", webdav_username: str = "", webdav_password: str = ""):
        """
        初始化WebDAV备份管理器
        
        Args:
            webdav_url: WebDAV服务器URL
            webdav_username: WebDAV用户名
            webdav_password: WebDAV密码
        """
        self.webdav_url = webdav_url
        self.webdav_username = webdav_username
        self.webdav_password = webdav_password
        self.backup_folder = "BettaFish"  # 备份文件夹名称
        self.client = None
        self.is_connected = False
        
        if WEBDAV_AVAILABLE and webdav_url and webdav_username and webdav_password:
            self._connect()
    
    def _connect(self) -> bool:
        """连接到WebDAV服务器"""
        if not WEBDAV_AVAILABLE:
            return False
            
        try:
            options = {
                'webdav_hostname': self.webdav_url,
                'webdav_login': self.webdav_username,
                'webdav_password': self.webdav_password,
                'webdav_timeout': 30
            }
            self.client = Client(options)
            
            # 测试连接
            self.client.list()
            
            # 确保BettaFish文件夹存在
            if not self.client.check(self.backup_folder):
                self.client.mkdir(self.backup_folder)
                print(f"WebDAV: 创建备份文件夹 {self.backup_folder}")
            
            self.is_connected = True
            print("WebDAV: 连接成功")
            return True
            
        except Exception as e:
            print(f"WebDAV连接失败: {e}")
            self.is_connected = False
            return False
    
    def save_config_to_webdav(self, config_data: Dict[str, Any], filename: str = None) -> Tuple[bool, str]:
        """
        保存配置到WebDAV
        
        Args:
            config_data: 配置数据
            filename: 文件名（可选，默认自动生成带时间戳的文件名）
            
        Returns:
            (是否成功, 消息)
        """
        if not self.is_connected:
            if not self._connect():
                return False, "WebDAV未连接或连接失败"
        
        try:
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"weiyu_config_{timestamp}.json"
            
            # 添加元数据
            backup_data = {
                "version": "1.0",
                "backup_time": datetime.now().isoformat(),
                "config": config_data
            }
            
            # 转换为JSON字符串
            json_data = json.dumps(backup_data, ensure_ascii=False, indent=2)
            
            # 上传到WebDAV
            remote_path = f"{self.backup_folder}/{filename}"
            
            # 写入临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as tmp:
                tmp.write(json_data)
                tmp_path = tmp.name
            
            try:
                self.client.upload_sync(remote_path=remote_path, local_path=tmp_path)
                return True, f"配置已备份到 WebDAV: {remote_path}"
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            return False, f"备份失败: {str(e)}"
    
    def load_config_from_webdav(self, filename: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        从WebDAV加载配置
        
        Args:
            filename: 文件名
            
        Returns:
            (是否成功, 配置数据, 消息)
        """
        if not self.is_connected:
            if not self._connect():
                return False, {}, "WebDAV未连接或连接失败"
        
        try:
            remote_path = f"{self.backup_folder}/{filename}"
            
            # 检查文件是否存在
            if not self.client.check(remote_path):
                return False, {}, f"文件不存在: {filename}"
            
            # 下载到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as tmp:
                tmp_path = tmp.name
            
            try:
                self.client.download_sync(remote_path=remote_path, local_path=tmp_path)
                
                # 读取配置
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                # 验证数据格式
                if 'config' not in backup_data:
                    return False, {}, "无效的备份文件格式"
                
                return True, backup_data['config'], f"配置已从 WebDAV 恢复: {filename}"
                
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            return False, {}, f"加载失败: {str(e)}"
    
    def list_backups(self) -> Tuple[bool, list, str]:
        """
        列出所有备份文件
        
        Returns:
            (是否成功, 文件列表, 消息)
        """
        if not self.is_connected:
            if not self._connect():
                return False, [], "WebDAV未连接或连接失败"
        
        try:
            files = self.client.list(self.backup_folder)
            
            # 过滤JSON文件并排序
            json_files = [f for f in files if f.endswith('.json')]
            json_files.sort(reverse=True)  # 最新的在前
            
            # 获取文件信息
            file_list = []
            for filename in json_files:
                try:
                    remote_path = f"{self.backup_folder}/{filename}"
                    info = self.client.info(remote_path)
                    file_list.append({
                        'filename': filename,
                        'size': info.get('size', 0),
                        'modified': info.get('modified', ''),
                        'display_name': filename.replace('weiyu_config_', '').replace('.json', '')
                    })
                except:
                    pass
            
            return True, file_list, f"找到 {len(file_list)} 个备份文件"
            
        except Exception as e:
            return False, [], f"列表失败: {str(e)}"
    
    def delete_backup(self, filename: str) -> Tuple[bool, str]:
        """
        删除备份文件
        
        Args:
            filename: 文件名
            
        Returns:
            (是否成功, 消息)
        """
        if not self.is_connected:
            if not self._connect():
                return False, "WebDAV未连接或连接失败"
        
        try:
            remote_path = f"{self.backup_folder}/{filename}"
            
            if not self.client.check(remote_path):
                return False, f"文件不存在: {filename}"
            
            self.client.clean(remote_path)
            return True, f"备份已删除: {filename}"
            
        except Exception as e:
            return False, f"删除失败: {str(e)}"


# 创建全局实例
_webdav_manager = None


def get_webdav_manager(webdav_url: str = "", webdav_username: str = "", webdav_password: str = "") -> WebDAVBackupManager:
    """获取WebDAV管理器实例"""
    global _webdav_manager
    
    if _webdav_manager is None or (webdav_url and webdav_username):
        _webdav_manager = WebDAVBackupManager(webdav_url, webdav_username, webdav_password)
    
    return _webdav_manager


def save_config_to_local(config_data: Dict[str, Any], filepath: str) -> Tuple[bool, str]:
    """
    保存配置到本地文件
    
    Args:
        config_data: 配置数据
        filepath: 文件路径
        
    Returns:
        (是否成功, 消息)
    """
    try:
        backup_data = {
            "version": "1.0",
            "backup_time": datetime.now().isoformat(),
            "config": config_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return True, f"配置已保存到: {filepath}"
        
    except Exception as e:
        return False, f"保存失败: {str(e)}"


def load_config_from_local(filepath: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    从本地文件加载配置
    
    Args:
        filepath: 文件路径
        
    Returns:
        (是否成功, 配置数据, 消息)
    """
    try:
        if not os.path.exists(filepath):
            return False, {}, f"文件不存在: {filepath}"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        if 'config' not in backup_data:
            return False, {}, "无效的备份文件格式"
        
        return True, backup_data['config'], f"配置已从本地恢复: {filepath}"
        
    except Exception as e:
        return False, {}, f"加载失败: {str(e)}"
