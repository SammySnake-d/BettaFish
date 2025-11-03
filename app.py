"""
Flask主应用 - 统一管理三个Streamlit应用
"""

import os
import sys
import subprocess
import time
import json
import threading
from datetime import datetime
from queue import Queue, Empty
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import signal
import atexit
import requests
import logging
import importlib
from pathlib import Path

# 导入ReportEngine
try:
    from ReportEngine.flask_interface import report_bp, initialize_report_engine
    REPORT_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"ReportEngine导入失败: {e}")
    REPORT_ENGINE_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dedicated-to-creating-a-concise-and-versatile-public-opinion-analysis-platform'
socketio = SocketIO(app, cors_allowed_origins="*")

# 注册ReportEngine Blueprint
if REPORT_ENGINE_AVAILABLE:
    app.register_blueprint(report_bp, url_prefix='/api/report')
    print("ReportEngine接口已注册")
else:
    print("ReportEngine不可用，跳过接口注册")

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 创建日志目录
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# 初始化ForumEngine的forum.log文件
def init_forum_log():
    """初始化forum.log文件"""
    try:
        forum_log_file = LOG_DIR / "forum.log"
        # 检查文件不存在则创建并且写一个开始，存在就清空写一个开始
        if not forum_log_file.exists():
            with open(forum_log_file, 'w', encoding='utf-8') as f:
                start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"=== ForumEngine 系统初始化 - {start_time} ===\n")
            print(f"ForumEngine: forum.log 已初始化")
        else:
            with open(forum_log_file, 'w', encoding='utf-8') as f:
                start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"=== ForumEngine 系统初始化 - {start_time} ===\n")
            print(f"ForumEngine: forum.log 已初始化")
    except Exception as e:
        print(f"ForumEngine: 初始化forum.log失败: {e}")

# 初始化forum.log
init_forum_log()

# 启动ForumEngine智能监控
def start_forum_engine():
    """启动ForumEngine论坛"""
    try:
        from ForumEngine.monitor import start_forum_monitoring
        print("ForumEngine: 启动论坛...")
        success = start_forum_monitoring()
        if not success:
            print("ForumEngine: 论坛启动失败")
    except Exception as e:
        print(f"ForumEngine: 启动论坛失败: {e}")

# 停止ForumEngine智能监控
def stop_forum_engine():
    """停止ForumEngine论坛"""
    try:
        from ForumEngine.monitor import stop_forum_monitoring
        print("ForumEngine: 停止论坛...")
        stop_forum_monitoring()
        print("ForumEngine: 论坛已停止")
    except Exception as e:
        print(f"ForumEngine: 停止论坛失败: {e}")

def parse_forum_log_line(line):
    """解析forum.log行内容，提取对话信息"""
    import re
    
    # 匹配格式: [时间] [来源] 内容
    pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s*\[([A-Z]+)\]\s*(.*)'
    match = re.match(pattern, line)
    
    if match:
        timestamp, source, content = match.groups()
        
        # 过滤掉系统消息和空内容
        if source == 'SYSTEM' or not content.strip():
            return None
        
        # 只处理三个Engine的消息
        if source not in ['QUERY', 'INSIGHT', 'MEDIA']:
            return None
        
        # 根据来源确定消息类型和发送者
        message_type = 'agent'
        sender = f'{source} Engine'
        
        return {
            'type': message_type,
            'sender': sender,
            'content': content.strip(),
            'timestamp': timestamp,
            'source': source
        }
    
    return None

# Forum日志监听器
def monitor_forum_log():
    """监听forum.log文件变化并推送到前端"""
    import time
    from pathlib import Path
    
    forum_log_file = LOG_DIR / "forum.log"
    last_position = 0
    processed_lines = set()  # 用于跟踪已处理的行，避免重复
    
    # 如果文件存在，获取初始位置
    if forum_log_file.exists():
        with open(forum_log_file, 'r', encoding='utf-8', errors='ignore') as f:
            # 初始化时读取所有现有行，避免重复处理
            existing_lines = f.readlines()
            for line in existing_lines:
                line_hash = hash(line.strip())
                processed_lines.add(line_hash)
            last_position = f.tell()
    
    while True:
        try:
            if forum_log_file.exists():
                with open(forum_log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    
                    if new_lines:
                        for line in new_lines:
                            line = line.rstrip('\n\r')
                            if line.strip():
                                line_hash = hash(line.strip())
                                
                                # 避免重复处理同一行
                                if line_hash in processed_lines:
                                    continue
                                
                                processed_lines.add(line_hash)
                                
                                # 解析日志行并发送forum消息
                                parsed_message = parse_forum_log_line(line)
                                if parsed_message:
                                    socketio.emit('forum_message', parsed_message)
                                
                                # 只有在控制台显示forum时才发送控制台消息
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                formatted_line = f"[{timestamp}] {line}"
                                socketio.emit('console_output', {
                                    'app': 'forum',
                                    'line': formatted_line
                                })
                        
                        last_position = f.tell()
                        
                        # 清理processed_lines集合，避免内存泄漏（保留最近1000行的哈希）
                        if len(processed_lines) > 1000:
                            processed_lines.clear()
            
            time.sleep(1)  # 每秒检查一次
        except Exception as e:
            print(f"Forum日志监听错误: {e}")
            time.sleep(5)

# 启动Forum日志监听线程
forum_monitor_thread = threading.Thread(target=monitor_forum_log, daemon=True)
forum_monitor_thread.start()

# 全局变量存储进程信息
processes = {
    'insight': {'process': None, 'port': 8501, 'status': 'stopped', 'output': [], 'log_file': None},
    'media': {'process': None, 'port': 8502, 'status': 'stopped', 'output': [], 'log_file': None},
    'query': {'process': None, 'port': 8503, 'status': 'stopped', 'output': [], 'log_file': None},
    'forum': {'process': None, 'port': None, 'status': 'running', 'output': [], 'log_file': None}  # Forum始终运行
}

# 输出队列
output_queues = {
    'insight': Queue(),
    'media': Queue(),
    'query': Queue(),
    'forum': Queue()
}

def write_log_to_file(app_name, line):
    """将日志写入文件"""
    try:
        log_file_path = LOG_DIR / f"{app_name}.log"
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
            f.flush()
    except Exception as e:
        print(f"Error writing log for {app_name}: {e}")

def read_log_from_file(app_name, tail_lines=None):
    """从文件读取日志"""
    try:
        log_file_path = LOG_DIR / f"{app_name}.log"
        if not log_file_path.exists():
            return []
        
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = [line.rstrip('\n\r') for line in lines if line.strip()]
            
            if tail_lines:
                return lines[-tail_lines:]
            return lines
    except Exception as e:
        print(f"Error reading log for {app_name}: {e}")
        return []

def read_process_output(process, app_name):
    """读取进程输出并写入文件"""
    import select
    import sys
    
    while True:
        try:
            if process.poll() is not None:
                # 进程结束，读取剩余输出
                remaining_output = process.stdout.read()
                if remaining_output:
                    lines = remaining_output.decode('utf-8', errors='replace').split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            formatted_line = f"[{timestamp}] {line}"
                            write_log_to_file(app_name, formatted_line)
                            socketio.emit('console_output', {
                                'app': app_name,
                                'line': formatted_line
                            })
                break
            
            # 使用非阻塞读取
            if sys.platform == 'win32':
                # Windows下使用不同的方法
                output = process.stdout.readline()
                if output:
                    line = output.decode('utf-8', errors='replace').strip()
                    if line:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        formatted_line = f"[{timestamp}] {line}"
                        
                        # 写入日志文件
                        write_log_to_file(app_name, formatted_line)
                        
                        # 发送到前端
                        socketio.emit('console_output', {
                            'app': app_name,
                            'line': formatted_line
                        })
                else:
                    # 没有输出时短暂休眠
                    time.sleep(0.1)
            else:
                # Unix系统使用select
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    output = process.stdout.readline()
                    if output:
                        line = output.decode('utf-8', errors='replace').strip()
                        if line:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            formatted_line = f"[{timestamp}] {line}"
                            
                            # 写入日志文件
                            write_log_to_file(app_name, formatted_line)
                            
                            # 发送到前端
                            socketio.emit('console_output', {
                                'app': app_name,
                                'line': formatted_line
                            })
                            
        except Exception as e:
            error_msg = f"Error reading output for {app_name}: {e}"
            print(error_msg)
            write_log_to_file(app_name, f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
            break

def start_streamlit_app(app_name, script_path, port):
    """启动Streamlit应用"""
    try:
        if processes[app_name]['process'] is not None:
            return False, "应用已经在运行"
        
        # 检查文件是否存在
        if not os.path.exists(script_path):
            return False, f"文件不存在: {script_path}"
        
        # 清空之前的日志文件
        log_file_path = LOG_DIR / f"{app_name}.log"
        if log_file_path.exists():
            log_file_path.unlink()
        
        # 创建启动日志
        start_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 启动 {app_name} 应用..."
        write_log_to_file(app_name, start_msg)
        
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            script_path,
            '--server.port', str(port),
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            # '--logger.level', 'debug',  # 增加日志详细程度
            '--logger.level', 'info',
            '--server.enableCORS', 'false'
        ]
        
        # 设置环境变量确保UTF-8编码和减少缓冲
        env = os.environ.copy()
        env.update({
            'PYTHONIOENCODING': 'utf-8',
            'PYTHONUTF8': '1',
            'LANG': 'en_US.UTF-8',
            'LC_ALL': 'en_US.UTF-8',
            'PYTHONUNBUFFERED': '1',  # 禁用Python缓冲
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false'
        })
        
        # 使用当前工作目录而不是脚本目录
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,  # 无缓冲
            universal_newlines=False,
            cwd=os.getcwd(),
            env=env,
            encoding=None,  # 让我们手动处理编码
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        processes[app_name]['process'] = process
        processes[app_name]['status'] = 'starting'
        processes[app_name]['output'] = []
        
        # 启动输出读取线程
        output_thread = threading.Thread(
            target=read_process_output,
            args=(process, app_name),
            daemon=True
        )
        output_thread.start()
        
        return True, f"{app_name} 应用启动中..."
        
    except Exception as e:
        error_msg = f"启动失败: {str(e)}"
        write_log_to_file(app_name, f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
        return False, error_msg

def stop_streamlit_app(app_name):
    """停止Streamlit应用"""
    try:
        if processes[app_name]['process'] is None:
            return False, "应用未运行"
        
        process = processes[app_name]['process']
        process.terminate()
        
        # 等待进程结束
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        processes[app_name]['process'] = None
        processes[app_name]['status'] = 'stopped'
        
        return True, f"{app_name} 应用已停止"
        
    except Exception as e:
        return False, f"停止失败: {str(e)}"

def check_app_status():
    """检查应用状态"""
    for app_name, info in processes.items():
        if info['process'] is not None:
            if info['process'].poll() is None:
                # 进程仍在运行，检查端口是否可访问
                try:
                    response = requests.get(f"http://localhost:{info['port']}", timeout=2)
                    if response.status_code == 200:
                        info['status'] = 'running'
                    else:
                        info['status'] = 'starting'
                except requests.exceptions.RequestException:
                    info['status'] = 'starting'
                except Exception:
                    info['status'] = 'starting'
            else:
                # 进程已结束
                info['process'] = None
                info['status'] = 'stopped'

def wait_for_app_startup(app_name, max_wait_time=30):
    """等待应用启动完成"""
    import time
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        info = processes[app_name]
        if info['process'] is None:
            return False, "进程已停止"
        
        if info['process'].poll() is not None:
            return False, "进程启动失败"
        
        try:
            response = requests.get(f"http://localhost:{info['port']}", timeout=2)
            if response.status_code == 200:
                info['status'] = 'running'
                return True, "启动成功"
        except:
            pass
        
        time.sleep(1)
    
    return False, "启动超时"

def cleanup_processes():
    """清理所有进程"""
    for app_name in processes:
        stop_streamlit_app(app_name)

# 注册清理函数
atexit.register(cleanup_processes)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """获取所有应用状态"""
    check_app_status()
    return jsonify({
        app_name: {
            'status': info['status'],
            'port': info['port'],
            'output_lines': len(info['output'])
        }
        for app_name, info in processes.items()
    })

@app.route('/api/start/<app_name>')
def start_app(app_name):
    """启动指定应用"""
    if app_name not in processes:
        return jsonify({'success': False, 'message': '未知应用'})
    
    script_paths = {
        'insight': 'SingleEngineApp/insight_engine_streamlit_app.py',
        'media': 'SingleEngineApp/media_engine_streamlit_app.py',
        'query': 'SingleEngineApp/query_engine_streamlit_app.py'
    }
    
    success, message = start_streamlit_app(
        app_name, 
        script_paths[app_name], 
        processes[app_name]['port']
    )
    
    
    if success:
        # 等待应用启动
        startup_success, startup_message = wait_for_app_startup(app_name, 15)
        if not startup_success:
            message += f" 但启动检查失败: {startup_message}"
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/stop/<app_name>')
def stop_app(app_name):
    """停止指定应用"""
    if app_name not in processes:
        return jsonify({'success': False, 'message': '未知应用'})
    
    success, message = stop_streamlit_app(app_name)
    return jsonify({'success': success, 'message': message})

@app.route('/api/output/<app_name>')
def get_output(app_name):
    """获取应用输出"""
    if app_name not in processes:
        return jsonify({'success': False, 'message': '未知应用'})
    
    # 特殊处理Forum Engine
    if app_name == 'forum':
        try:
            forum_log_content = read_log_from_file('forum')
            return jsonify({
                'success': True,
                'output': forum_log_content,
                'total_lines': len(forum_log_content)
            })
        except Exception as e:
            return jsonify({'success': False, 'message': f'读取forum日志失败: {str(e)}'})
    
    # 从文件读取完整日志
    output_lines = read_log_from_file(app_name)
    
    return jsonify({
        'success': True,
        'output': output_lines
    })

@app.route('/api/test_log/<app_name>')
def test_log(app_name):
    """测试日志写入功能"""
    if app_name not in processes:
        return jsonify({'success': False, 'message': '未知应用'})
    
    # 写入测试消息
    test_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 测试日志消息 - {datetime.now()}"
    write_log_to_file(app_name, test_msg)
    
    # 通过Socket.IO发送
    socketio.emit('console_output', {
        'app': app_name,
        'line': test_msg
    })
    
    return jsonify({
        'success': True,
        'message': f'测试消息已写入 {app_name} 日志'
    })

@app.route('/api/forum/start')
def start_forum_monitoring_api():
    """手动启动ForumEngine论坛"""
    try:
        from ForumEngine.monitor import start_forum_monitoring
        success = start_forum_monitoring()
        if success:
            return jsonify({'success': True, 'message': 'ForumEngine论坛已启动'})
        else:
            return jsonify({'success': False, 'message': 'ForumEngine论坛启动失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'启动论坛失败: {str(e)}'})

@app.route('/api/forum/stop')
def stop_forum_monitoring_api():
    """手动停止ForumEngine论坛"""
    try:
        from ForumEngine.monitor import stop_forum_monitoring
        stop_forum_monitoring()
        return jsonify({'success': True, 'message': 'ForumEngine论坛已停止'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'停止论坛失败: {str(e)}'})

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    try:
        config_module = importlib.import_module('config')
        config_module = importlib.reload(config_module)
    except Exception as e:
        return jsonify({'success': False, 'error': f'加载配置失败: {e}'})

    config_data = {
        'database': {
            'host': getattr(config_module, 'DB_HOST', ''),
            'port': getattr(config_module, 'DB_PORT', 3306),
            'user': getattr(config_module, 'DB_USER', ''),
            'password': getattr(config_module, 'DB_PASSWORD', ''),
            'name': getattr(config_module, 'DB_NAME', ''),
            'charset': getattr(config_module, 'DB_CHARSET', 'utf8mb4')
        },
        'engines': {
            'insight': {
                'api_key': getattr(config_module, 'INSIGHT_ENGINE_API_KEY', ''),
                'base_url': getattr(config_module, 'INSIGHT_ENGINE_BASE_URL', ''),
                'model_name': getattr(config_module, 'INSIGHT_ENGINE_MODEL_NAME', '')
            },
            'media': {
                'api_key': getattr(config_module, 'MEDIA_ENGINE_API_KEY', ''),
                'base_url': getattr(config_module, 'MEDIA_ENGINE_BASE_URL', ''),
                'model_name': getattr(config_module, 'MEDIA_ENGINE_MODEL_NAME', '')
            },
            'query': {
                'api_key': getattr(config_module, 'QUERY_ENGINE_API_KEY', ''),
                'base_url': getattr(config_module, 'QUERY_ENGINE_BASE_URL', ''),
                'model_name': getattr(config_module, 'QUERY_ENGINE_MODEL_NAME', '')
            },
            'report': {
                'api_key': getattr(config_module, 'REPORT_ENGINE_API_KEY', ''),
                'base_url': getattr(config_module, 'REPORT_ENGINE_BASE_URL', ''),
                'model_name': getattr(config_module, 'REPORT_ENGINE_MODEL_NAME', '')
            },
            'forum_host': {
                'api_key': getattr(config_module, 'FORUM_HOST_API_KEY', ''),
                'base_url': getattr(config_module, 'FORUM_HOST_BASE_URL', ''),
                'model_name': getattr(config_module, 'FORUM_HOST_MODEL_NAME', '')
            },
            'keyword_optimizer': {
                'api_key': getattr(config_module, 'KEYWORD_OPTIMIZER_API_KEY', ''),
                'base_url': getattr(config_module, 'KEYWORD_OPTIMIZER_BASE_URL', ''),
                'model_name': getattr(config_module, 'KEYWORD_OPTIMIZER_MODEL_NAME', '')
            }
        },
        'tools': {
            'tavily_api_key': getattr(config_module, 'TAVILY_API_KEY', ''),
            'bocha_api_key': getattr(config_module, 'BOCHA_WEB_SEARCH_API_KEY', '')
        },
        'crawler': {
            'deepseek_api_key': getattr(config_module, 'DEEPSEEK_API_KEY', '')
        },
        'webdav': {
            'url': getattr(config_module, 'WEBDAV_URL', ''),
            'username': getattr(config_module, 'WEBDAV_USERNAME', ''),
            'password': getattr(config_module, 'WEBDAV_PASSWORD', '')
        },
        'advanced': {
            'query_max_reflections': getattr(config_module, 'QUERY_ENGINE_MAX_REFLECTIONS', 2),
            'query_max_search_results': getattr(config_module, 'QUERY_ENGINE_MAX_SEARCH_RESULTS', 20),
            'query_max_content_length': getattr(config_module, 'QUERY_ENGINE_MAX_CONTENT_LENGTH', 20000),
            'media_max_reflections': getattr(config_module, 'MEDIA_ENGINE_MAX_REFLECTIONS', 2),
            'media_max_content_length': getattr(config_module, 'MEDIA_ENGINE_MAX_CONTENT_LENGTH', 20000),
            'insight_max_reflections': getattr(config_module, 'INSIGHT_ENGINE_MAX_REFLECTIONS', 3),
            'insight_max_content_length': getattr(config_module, 'INSIGHT_ENGINE_MAX_CONTENT_LENGTH', 500000),
            'insight_search_globally_limit': getattr(config_module, 'INSIGHT_ENGINE_DEFAULT_SEARCH_TOPIC_GLOBALLY_LIMIT', 50),
            'insight_get_comments_limit': getattr(config_module, 'INSIGHT_ENGINE_DEFAULT_GET_COMMENTS_LIMIT', 500),
            'insight_max_results_for_llm': getattr(config_module, 'INSIGHT_ENGINE_MAX_SEARCH_RESULTS_FOR_LLM', 0)
        },
        'sentiment': {
            'enabled': getattr(config_module, 'SENTIMENT_ANALYSIS_ENABLED', True),
            'model_type': getattr(config_module, 'SENTIMENT_MODEL_TYPE', 'multilingual'),
            'confidence_threshold': getattr(config_module, 'SENTIMENT_CONFIDENCE_THRESHOLD', 0.8),
            'batch_size': getattr(config_module, 'SENTIMENT_BATCH_SIZE', 32),
            'max_sequence_length': getattr(config_module, 'SENTIMENT_MAX_SEQUENCE_LENGTH', 512)
        }
    }

    return jsonify({'success': True, 'config': config_data})


@app.route('/api/config', methods=['POST'])
def save_config():
    """保存配置信息"""
    try:
        config_data = request.json or {}
        if not config_data:
            return jsonify({'success': False, 'error': '无效的配置数据'})

        config_file = Path('config.py')
        if not config_file.exists():
            return jsonify({'success': False, 'error': '配置文件不存在'})

        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        def update_line(line, var_name, value, is_number=False):
            if f'{var_name}' not in line:
                return line
            stripped = line.rstrip('\n')
            lstripped = stripped.lstrip()
            if not (lstripped.startswith(f'{var_name} ') or lstripped.startswith(f'{var_name}=')):
                return line
            prefix_whitespace = stripped[:len(stripped) - len(lstripped)]
            eq_index = lstripped.find('=')
            if eq_index == -1:
                return line
            before_eq = lstripped[:eq_index + 1]
            after_eq = lstripped[eq_index + 1:]
            comment = ''
            if '#' in after_eq:
                value_part, comment = after_eq.split('#', 1)
                comment = '#' + comment
            else:
                value_part = after_eq
            leading_len = len(value_part) - len(value_part.lstrip())
            trailing_len = len(value_part) - len(value_part.rstrip())
            leading = value_part[:leading_len] if leading_len > 0 else ' '
            trailing = value_part[len(value_part) - trailing_len:] if trailing_len > 0 else ''
            if is_number:
                new_value = str(value)
            else:
                escaped_value = str(value).replace('\\', '\\\\').replace('"', '\\"')
                new_value = f'"{escaped_value}"'
            return f'{prefix_whitespace}{before_eq}{leading}{new_value}{trailing}{comment}\n'

        db_conf = config_data.get('database', {})
        engines_conf = config_data.get('engines', {})
        tools_conf = config_data.get('tools', {})
        crawler_conf = config_data.get('crawler', {})
        webdav_conf = config_data.get('webdav', {})
        advanced_conf = config_data.get('advanced', {})
        sentiment_conf = config_data.get('sentiment', {})

        port_value = db_conf.get('port', 3306)
        try:
            port_value = int(port_value)
        except (TypeError, ValueError):
            port_value = 3306

        updated_lines = []
        for line in lines:
            updated_line = line

            if db_conf:
                updated_line = update_line(updated_line, 'DB_HOST', db_conf.get('host', ''))
                updated_line = update_line(updated_line, 'DB_PORT', port_value, is_number=True)
                updated_line = update_line(updated_line, 'DB_USER', db_conf.get('user', ''))
                updated_line = update_line(updated_line, 'DB_PASSWORD', db_conf.get('password', ''))
                updated_line = update_line(updated_line, 'DB_NAME', db_conf.get('name', ''))
                updated_line = update_line(updated_line, 'DB_CHARSET', db_conf.get('charset', 'utf8mb4'))

            if engines_conf:
                insight_conf = engines_conf.get('insight', {})
                if insight_conf:
                    updated_line = update_line(updated_line, 'INSIGHT_ENGINE_API_KEY', insight_conf.get('api_key', ''))
                    updated_line = update_line(updated_line, 'INSIGHT_ENGINE_BASE_URL', insight_conf.get('base_url', ''))
                    updated_line = update_line(updated_line, 'INSIGHT_ENGINE_MODEL_NAME', insight_conf.get('model_name', ''))

                media_conf = engines_conf.get('media', {})
                if media_conf:
                    updated_line = update_line(updated_line, 'MEDIA_ENGINE_API_KEY', media_conf.get('api_key', ''))
                    updated_line = update_line(updated_line, 'MEDIA_ENGINE_BASE_URL', media_conf.get('base_url', ''))
                    updated_line = update_line(updated_line, 'MEDIA_ENGINE_MODEL_NAME', media_conf.get('model_name', ''))

                query_conf = engines_conf.get('query', {})
                if query_conf:
                    updated_line = update_line(updated_line, 'QUERY_ENGINE_API_KEY', query_conf.get('api_key', ''))
                    updated_line = update_line(updated_line, 'QUERY_ENGINE_BASE_URL', query_conf.get('base_url', ''))
                    updated_line = update_line(updated_line, 'QUERY_ENGINE_MODEL_NAME', query_conf.get('model_name', ''))

                report_conf = engines_conf.get('report', {})
                if report_conf:
                    updated_line = update_line(updated_line, 'REPORT_ENGINE_API_KEY', report_conf.get('api_key', ''))
                    updated_line = update_line(updated_line, 'REPORT_ENGINE_BASE_URL', report_conf.get('base_url', ''))
                    updated_line = update_line(updated_line, 'REPORT_ENGINE_MODEL_NAME', report_conf.get('model_name', ''))

                forum_conf = engines_conf.get('forum_host', {})
                if forum_conf:
                    updated_line = update_line(updated_line, 'FORUM_HOST_API_KEY', forum_conf.get('api_key', ''))
                    updated_line = update_line(updated_line, 'FORUM_HOST_BASE_URL', forum_conf.get('base_url', ''))
                    updated_line = update_line(updated_line, 'FORUM_HOST_MODEL_NAME', forum_conf.get('model_name', ''))

                keyword_conf = engines_conf.get('keyword_optimizer', {})
                if keyword_conf:
                    updated_line = update_line(updated_line, 'KEYWORD_OPTIMIZER_API_KEY', keyword_conf.get('api_key', ''))
                    updated_line = update_line(updated_line, 'KEYWORD_OPTIMIZER_BASE_URL', keyword_conf.get('base_url', ''))
                    updated_line = update_line(updated_line, 'KEYWORD_OPTIMIZER_MODEL_NAME', keyword_conf.get('model_name', ''))

            if tools_conf:
                updated_line = update_line(updated_line, 'TAVILY_API_KEY', tools_conf.get('tavily_api_key', ''))
                updated_line = update_line(updated_line, 'BOCHA_WEB_SEARCH_API_KEY', tools_conf.get('bocha_api_key', ''))

            if crawler_conf:
                updated_line = update_line(updated_line, 'DEEPSEEK_API_KEY', crawler_conf.get('deepseek_api_key', ''))

            if webdav_conf:
                updated_line = update_line(updated_line, 'WEBDAV_URL', webdav_conf.get('url', ''))
                updated_line = update_line(updated_line, 'WEBDAV_USERNAME', webdav_conf.get('username', ''))
                updated_line = update_line(updated_line, 'WEBDAV_PASSWORD', webdav_conf.get('password', ''))

            if advanced_conf:
                updated_line = update_line(updated_line, 'QUERY_ENGINE_MAX_REFLECTIONS', advanced_conf.get('query_max_reflections', 2), is_number=True)
                updated_line = update_line(updated_line, 'QUERY_ENGINE_MAX_SEARCH_RESULTS', advanced_conf.get('query_max_search_results', 20), is_number=True)
                updated_line = update_line(updated_line, 'QUERY_ENGINE_MAX_CONTENT_LENGTH', advanced_conf.get('query_max_content_length', 20000), is_number=True)
                updated_line = update_line(updated_line, 'MEDIA_ENGINE_MAX_REFLECTIONS', advanced_conf.get('media_max_reflections', 2), is_number=True)
                updated_line = update_line(updated_line, 'MEDIA_ENGINE_MAX_CONTENT_LENGTH', advanced_conf.get('media_max_content_length', 20000), is_number=True)
                updated_line = update_line(updated_line, 'INSIGHT_ENGINE_MAX_REFLECTIONS', advanced_conf.get('insight_max_reflections', 3), is_number=True)
                updated_line = update_line(updated_line, 'INSIGHT_ENGINE_MAX_CONTENT_LENGTH', advanced_conf.get('insight_max_content_length', 500000), is_number=True)
                updated_line = update_line(updated_line, 'INSIGHT_ENGINE_DEFAULT_SEARCH_TOPIC_GLOBALLY_LIMIT', advanced_conf.get('insight_search_globally_limit', 50), is_number=True)
                updated_line = update_line(updated_line, 'INSIGHT_ENGINE_DEFAULT_GET_COMMENTS_LIMIT', advanced_conf.get('insight_get_comments_limit', 500), is_number=True)
                updated_line = update_line(updated_line, 'INSIGHT_ENGINE_MAX_SEARCH_RESULTS_FOR_LLM', advanced_conf.get('insight_max_results_for_llm', 0), is_number=True)

            if sentiment_conf:
                updated_line = update_line(updated_line, 'SENTIMENT_ANALYSIS_ENABLED', sentiment_conf.get('enabled', True), is_number=True)
                updated_line = update_line(updated_line, 'SENTIMENT_MODEL_TYPE', sentiment_conf.get('model_type', 'multilingual'))
                updated_line = update_line(updated_line, 'SENTIMENT_CONFIDENCE_THRESHOLD', sentiment_conf.get('confidence_threshold', 0.8), is_number=True)
                updated_line = update_line(updated_line, 'SENTIMENT_BATCH_SIZE', sentiment_conf.get('batch_size', 32), is_number=True)
                updated_line = update_line(updated_line, 'SENTIMENT_MAX_SEQUENCE_LENGTH', sentiment_conf.get('max_sequence_length', 512), is_number=True)

            updated_lines.append(updated_line)

        with open(config_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

        importlib.invalidate_caches()
        config_module = importlib.import_module('config')
        importlib.reload(config_module)

        return jsonify({'success': True, 'message': '配置已保存'})
    except Exception as e:
        logging.exception("保存配置失败")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/forum/log')
def get_forum_log():
    """获取ForumEngine的forum.log内容"""
    try:
        forum_log_file = LOG_DIR / "forum.log"
        if not forum_log_file.exists():
            return jsonify({
                'success': True,
                'log_lines': [],
                'parsed_messages': [],
                'total_lines': 0
            })
        
        with open(forum_log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            lines = [line.rstrip('\n\r') for line in lines if line.strip()]
        
        # 解析每一行日志并提取对话信息
        parsed_messages = []
        for line in lines:
            parsed_message = parse_forum_log_line(line)
            if parsed_message:
                parsed_messages.append(parsed_message)
        
        return jsonify({
            'success': True,
            'log_lines': lines,
            'parsed_messages': parsed_messages,
            'total_lines': len(lines)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'读取forum.log失败: {str(e)}'})

@app.route('/api/search', methods=['POST'])
def search():
    """统一搜索接口"""
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'success': False, 'message': '搜索查询不能为空'})
    
    # ForumEngine论坛已经在后台运行，会自动检测搜索活动
    # print("ForumEngine: 搜索请求已收到，论坛将自动检测日志变化")
    
    # 检查哪些应用正在运行
    check_app_status()
    running_apps = [name for name, info in processes.items() if info['status'] == 'running']
    
    if not running_apps:
        return jsonify({'success': False, 'message': '没有运行中的应用'})
    
    # 向运行中的应用发送搜索请求
    results = {}
    api_ports = {'insight': 8601, 'media': 8602, 'query': 8603}
    
    for app_name in running_apps:
        try:
            api_port = api_ports[app_name]
            # 调用Streamlit应用的API端点
            response = requests.post(
                f"http://localhost:{api_port}/api/search",
                json={'query': query},
                timeout=10
            )
            if response.status_code == 200:
                results[app_name] = response.json()
            else:
                results[app_name] = {'success': False, 'message': 'API调用失败'}
        except Exception as e:
            results[app_name] = {'success': False, 'message': str(e)}
    
    # 搜索完成后可以选择停止监控，或者让它继续运行以捕获后续的处理日志
    # 这里我们让监控继续运行，用户可以通过其他接口手动停止
    
    return jsonify({
        'success': True,
        'query': query,
        'results': results
    })

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    emit('status', 'Connected to Flask server')

@socketio.on('request_status')
def handle_status_request():
    """请求状态更新"""
    check_app_status()
    emit('status_update', {
        app_name: {
            'status': info['status'],
            'port': info['port']
        }
        for app_name, info in processes.items()
    })

if __name__ == '__main__':
    # 启动时自动启动所有Streamlit应用
    print("正在启动Streamlit应用...")
    
    # 先停止ForumEngine监控器，避免文件占用冲突
    print("停止ForumEngine监控器以避免文件冲突...")
    stop_forum_engine()
    
    script_paths = {
        'insight': 'SingleEngineApp/insight_engine_streamlit_app.py',
        'media': 'SingleEngineApp/media_engine_streamlit_app.py',
        'query': 'SingleEngineApp/query_engine_streamlit_app.py'
    }
    
    for app_name, script_path in script_paths.items():
        print(f"检查文件: {script_path}")
        if os.path.exists(script_path):
            print(f"启动 {app_name}...")
            success, message = start_streamlit_app(app_name, script_path, processes[app_name]['port'])
            print(f"{app_name}: {message}")
            
            if success:
                print(f"等待 {app_name} 启动完成...")
                startup_success, startup_message = wait_for_app_startup(app_name, 30)
                print(f"{app_name} 启动检查: {startup_message}")
        else:
            print(f"错误: {script_path} 不存在")
    
    start_forum_engine()
    
    # 初始化ReportEngine
    if REPORT_ENGINE_AVAILABLE:
        print("初始化ReportEngine...")
        if initialize_report_engine():
            print("ReportEngine初始化成功")
            print("ReportEngine文件基准已建立，开始监控文件变化")
        else:
            print("ReportEngine初始化失败")
    
    print("启动Flask服务器...")
    
    try:
        # 启动Flask应用
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n正在关闭应用...")
        cleanup_processes()
        
    
