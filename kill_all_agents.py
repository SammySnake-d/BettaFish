#!/usr/bin/env python3
"""
一键杀死所有 Agent 进程的脚本 (跨平台版本)
用于在更新代码前清理所有运行中的服务
支持 Windows、Linux 和 macOS
"""

import os
import sys
import signal
import psutil
import time
from typing import List, Set

# 定义所有使用的端口
PORTS = [5000, 8501, 8502, 8503, 8601, 8602, 8603]

# 定义要查找的进程关键字
PROCESS_KEYWORDS = [
    'streamlit',
    'app.py',
    'insight_engine',
    'media_engine',
    'query_engine'
]

def get_process_info(proc: psutil.Process) -> str:
    """获取进程的简要信息"""
    try:
        cmdline = ' '.join(proc.cmdline())
        if len(cmdline) > 80:
            cmdline = cmdline[:77] + '...'
        return f"PID={proc.pid}, 名称={proc.name()}, 命令={cmdline}"
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return f"PID={proc.pid}, 名称={proc.name()}"

def find_processes_by_port(port: int) -> List[psutil.Process]:
    """查找占用指定端口的进程"""
    processes = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port and conn.pid:
            try:
                proc = psutil.Process(conn.pid)
                if proc not in processes:
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return processes

def find_processes_by_keyword(keywords: List[str]) -> List[psutil.Process]:
    """查找包含指定关键字的进程"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.cmdline()).lower()
            name = proc.name().lower()
            
            for keyword in keywords:
                if keyword.lower() in cmdline or keyword.lower() in name:
                    if proc not in processes:
                        processes.append(proc)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def kill_process(proc: psutil.Process, force: bool = False) -> bool:
    """
    终止进程
    
    Args:
        proc: 要终止的进程
        force: 是否强制终止（SIGKILL）
    
    Returns:
        True 表示成功终止，False 表示失败
    """
    try:
        if not proc.is_running():
            return True
        
        if force:
            # 强制终止
            if sys.platform == 'win32':
                proc.kill()
            else:
                os.kill(proc.pid, signal.SIGKILL)
        else:
            # 优雅终止
            if sys.platform == 'win32':
                proc.terminate()
            else:
                os.kill(proc.pid, signal.SIGTERM)
        
        # 等待进程终止
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            return False
        
        return not proc.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return True  # 进程已不存在或无权访问

def main():
    """主函数"""
    print("=" * 50)
    print("开始停止所有 Agent 进程...")
    print("=" * 50)
    
    killed_count = 0
    all_processes: Set[psutil.Process] = set()
    
    # 1. 通过端口查找进程
    print("\n检查端口占用...")
    for port in PORTS:
        print(f"\n检查端口 {port}...")
        processes = find_processes_by_port(port)
        
        if not processes:
            print(f"  ✓ 端口 {port} 没有运行的进程")
        else:
            for proc in processes:
                all_processes.add(proc)
                print(f"  ⚠ 发现进程: {get_process_info(proc)}")
    
    # 2. 通过关键字查找进程
    print("\n" + "=" * 50)
    print("检查残留的 Streamlit 和 Flask 进程...")
    print("=" * 50)
    
    keyword_processes = find_processes_by_keyword(PROCESS_KEYWORDS)
    if keyword_processes:
        print("发现相关进程:")
        for proc in keyword_processes:
            all_processes.add(proc)
            print(f"  ⚠ {get_process_info(proc)}")
    else:
        print("  ✓ 没有找到相关进程")
    
    # 3. 终止所有找到的进程
    if not all_processes:
        print("\n" + "=" * 50)
        print("没有需要终止的进程")
        print("=" * 50)
        return
    
    print("\n" + "=" * 50)
    print(f"找到 {len(all_processes)} 个进程，开始终止...")
    print("=" * 50)
    
    for proc in all_processes:
        try:
            if not proc.is_running():
                continue
            
            print(f"\n  → 正在终止进程 {proc.pid} (SIGTERM)...")
            
            # 先尝试优雅终止
            if kill_process(proc, force=False):
                print(f"  ✓ 进程 {proc.pid} 已成功终止")
                killed_count += 1
            else:
                # 优雅终止失败，强制终止
                print(f"  → 进程未响应，强制杀死 (SIGKILL)...")
                if kill_process(proc, force=True):
                    print(f"  ✓ 进程 {proc.pid} 已强制终止")
                    killed_count += 1
                else:
                    print(f"  ✗ 无法杀死进程 {proc.pid}")
        except Exception as e:
            print(f"  ✗ 终止进程 {proc.pid} 时出错: {e}")
    
    print("\n" + "=" * 50)
    print("清理完成！")
    print(f"共终止 {killed_count} 个进程")
    print("=" * 50)
    print("\n提示: 现在可以安全地更新代码并重新启动应用\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)
