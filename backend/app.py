from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from config import Config
from .models.user import db
from .routes.auth import auth_bp
import pymysql
import sys
import os
import subprocess
import threading
import time
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

def test_database_connection():
    """测试数据库连接"""
    try:
        # 测试MySQL直接连接
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        conn.close()
        return True
    except Exception as e:
        print(f"\n❌ 数据库连接失败：{str(e)}")
        print("请检查：")
        print("1. MySQL服务是否启动")
        print(f"2. 数据库配置是否正确（主机：{Config.MYSQL_HOST}, 端口：{Config.MYSQL_PORT}）")
        print("3. 用户名和密码是否正确")
        return False

def create_app():
    # 首先测试数据库连接
    if not test_database_connection():
        print("\n❌ 后端启动失败：无法连接到数据库")
        sys.exit(1)

    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 爬虫进度存储
    crawler_tasks = {}
    
    def run_spider(task_id):
        """在后台运行爬虫"""
        try:
            # 更新任务状态为运行中
            crawler_tasks[task_id]['status'] = 'running'
            crawler_tasks[task_id]['start_time'] = datetime.now()
            crawler_tasks[task_id]['message'] = '爬虫开始工作，正在采集数据...'
            
            # 准备爬虫命令
            spider_path = os.path.join(project_root, 'crawler', 'spiders', 'wuhan_housing.py')
            output_path = os.path.join(project_root, 'data', 'raw', 'wuhan_housing.csv')
            
            # 检查爬虫文件是否存在
            if not os.path.exists(spider_path):
                raise FileNotFoundError(f'爬虫文件不存在: {spider_path}')
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 如果输出文件已存在，先删除它
            if os.path.exists(output_path):
                os.remove(output_path)
            
            print(f"启动爬虫，工作目录: {project_root}")
            print(f"爬虫文件路径: {spider_path}")
            
            # 构建爬虫命令
            command = [
                sys.executable,  # 使用当前Python解释器
                '-m', 'scrapy', 'runspider',
                spider_path,
                '-o', output_path,
                '-s', 'CLOSESPIDER_ITEMCOUNT=5400',
                '-s', 'FEED_EXPORT_ENCODING=utf-8'  # 设置输出文件编码
            ]
            
            # 启动爬虫进程
            env = os.environ.copy()
            env['PYTHONPATH'] = project_root  # 添加项目根目录到Python路径
            print(f"执行命令: {' '.join(command)}")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                cwd=project_root,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW  # 在Windows上不显示控制台窗口
            )
            
            # 更新任务信息
            crawler_tasks[task_id]['process'] = process
            
            # 监控爬虫进程
            last_count = 0
            no_progress_time = 0
            
            while True:
                if process.poll() is not None:  # 进程已结束
                    stdout, stderr = process.communicate()
                    print(f"爬虫进程结束，返回码: {process.returncode}")
                    print(f"标准输出: {stdout}")
                    print(f"错误输出: {stderr}")
                    
                    if process.returncode != 0:
                        crawler_tasks[task_id]['status'] = 'failed'
                        error_msg = f'爬虫执行失败，错误代码: {process.returncode}\n'
                        if stderr:
                            error_msg += f'错误信息: {stderr}'
                        crawler_tasks[task_id]['message'] = error_msg
                    break
                
                # 检查输出文件大小和行数
                try:
                    if os.path.exists(output_path):
                        # 尝试不同的编码方式读取文件
                        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
                        for encoding in encodings:
                            try:
                                with open(output_path, 'r', encoding=encoding) as f:
                                    line_count = sum(1 for _ in f)
                                    crawler_tasks[task_id]['count'] = line_count
                                    
                                    # 检查是否有新的进度
                                    if line_count > last_count:
                                        last_count = line_count
                                        no_progress_time = 0
                                        progress = min(line_count / 5400 * 100, 100)
                                        # 将进度值精确到3位小数
                                        progress = round(progress, 3)
                                        crawler_tasks[task_id]['progress'] = progress
                                        crawler_tasks[task_id]['message'] = f'已采集 {line_count} 条数据，总进度 {progress}%'
                                    else:
                                        no_progress_time += 1
                                        if no_progress_time >= 30:
                                            # 检查进程是否还在运行
                                            if process.poll() is None:
                                                process.terminate()  # 如果进程还在运行但没有进展，则终止它
                                            if line_count > 0:
                                                crawler_tasks[task_id]['status'] = 'completed'
                                                crawler_tasks[task_id]['message'] = f'数据采集完成，共采集 {line_count} 条数据'
                                                crawler_tasks[task_id]['progress'] = 100
                                            break
                                break  # 如果成功读取文件，跳出编码尝试循环
                            except UnicodeDecodeError:
                                continue  # 尝试下一个编码
                except Exception as e:
                    print(f"读取文件时出错: {str(e)}")
                
                time.sleep(1)
            
            # 检查进程退出状态
            if process.returncode == 0:
                if crawler_tasks[task_id]['status'] != 'completed':
                    crawler_tasks[task_id]['status'] = 'completed'
                    crawler_tasks[task_id]['message'] = f'数据采集完成，共采集 {crawler_tasks[task_id]["count"]} 条数据'
                    crawler_tasks[task_id]['progress'] = 100
            
        except Exception as e:
            print(f"爬虫运行错误: {str(e)}")
            crawler_tasks[task_id]['status'] = 'failed'
            crawler_tasks[task_id]['message'] = f'发生错误: {str(e)}'
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 在生产环境中使用更安全的密钥
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    jwt = JWTManager(app)
    
    # 初始化扩展
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://localhost:8081"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials", "X-Requested-With"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"],
            "max_age": 600
        }
    })
    
    # 添加全局OPTIONS请求处理
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
            
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 创建数据库表
    with app.app_context():
        try:
            db.create_all()
            print("\n✅ 数据库表创建成功！")
        except Exception as e:
            print(f"\n❌ 数据库表创建失败：{str(e)}")
            sys.exit(1)
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok'}
    
    # 爬虫相关路由
    @app.route('/api/crawler/start', methods=['POST'])
    def start_crawler():
        try:
            # 检查是否有正在运行的任务
            for task_id, task in crawler_tasks.items():
                if task['status'] == 'running':
                    return jsonify({
                        'message': '已有爬虫任务正在运行',
                        'task_id': task_id
                    }), 400
            
            # 生成任务ID
            task_id = datetime.now().strftime('%Y%m%d%H%M%S')
            print(f"创建新任务: {task_id}")
            
            # 初始化任务信息
            crawler_tasks[task_id] = {
                'status': 'starting',
                'progress': 0,
                'count': 0,
                'message': '正在启动爬虫...',
                'start_time': datetime.now(),
                'process': None
            }
            
            print(f"当前活动任务: {list(crawler_tasks.keys())}")
            
            try:
                # 在新线程中运行爬虫
                thread = threading.Thread(target=run_spider, args=(task_id,))
                thread.daemon = True  # 设置为守护线程
                thread.start()
                
                print(f"爬虫线程已启动: {task_id}")
                
                return jsonify({
                    'message': '爬虫启动成功',
                    'task_id': task_id
                }), 200
                
            except Exception as e:
                print(f"启动爬虫线程失败: {str(e)}")
                # 如果线程启动失败，清理任务信息
                if task_id in crawler_tasks:
                    del crawler_tasks[task_id]
                raise
            
        except Exception as e:
            print(f"启动爬虫失败: {str(e)}")
            return jsonify({
                'message': f'启动爬虫失败: {str(e)}'
            }), 500

    @app.route('/api/crawler/progress/<task_id>', methods=['GET'])
    def get_crawler_progress(task_id):
        print(f"检查任务进度: {task_id}")
        print(f"当前活动任务: {list(crawler_tasks.keys())}")
        
        if task_id not in crawler_tasks:
            return jsonify({
                'status': 'not_found',
                'message': '任务不存在',
                'progress': 0,
                'count': 0,
                'elapsed_time': 0
            }), 404
        
        task = crawler_tasks[task_id]
        
        # 计算运行时间
        elapsed_time = None
        if task['start_time']:
            elapsed_time = (datetime.now() - task['start_time']).total_seconds()
        
        response_data = {
            'status': task['status'],
            'progress': task['progress'],
            'count': task['count'],
            'message': task['message'],
            'elapsed_time': elapsed_time
        }
        
        print(f"任务状态: {response_data}")
        return jsonify(response_data), 200

    @app.route('/api/crawler/stop', methods=['POST'])
    def stop_crawler():
        try:
            stopped = False
            for task_id, task in crawler_tasks.items():
                if task['status'] == 'running' and task['process']:
                    # 终止爬虫进程及其所有子进程
                    try:
                        import psutil
                        parent = psutil.Process(task['process'].pid)
                        for child in parent.children(recursive=True):
                            child.terminate()
                        parent.terminate()
                    except:
                        # 如果psutil不可用，直接使用terminate
                        task['process'].terminate()
                    
                    # 等待进程结束
                    task['process'].wait(timeout=5)
                    
                    # 更新任务状态
                    task['status'] = 'stopped'
                    task['message'] = '爬虫已手动停止'
                    task['progress'] = 0
                    stopped = True
            
            if stopped:
                return jsonify({
                    'message': '爬虫已停止'
                }), 200
            else:
                return jsonify({
                    'message': '没有正在运行的爬虫'
                }), 404
                
        except Exception as e:
            return jsonify({
                'message': f'停止爬虫失败: {str(e)}'
            }), 500
            
    return app

app = create_app()

def print_startup_message():
    """打印启动信息"""
    print("\n" + "=" * 60)
    print("🚀 后端服务已启动！")
    print("=" * 60)
    print("📝 API接口:")
    print("- 健康检查: http://localhost:5000/api/health")
    print("- 用户注册: http://localhost:5000/api/auth/register")
    print("- 用户登录: http://localhost:5000/api/auth/login")
    print("\n⚠️ 请确保运行前端服务！")
    print("在前端目录下运行：")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run serve")
    print("=" * 60 + "\n")

# 处理OPTIONS请求
@app.route('/api/crawler/start', methods=['OPTIONS'])
@app.route('/api/crawler/stop', methods=['OPTIONS'])
@app.route('/api/crawler/progress/<task_id>', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    print_startup_message()
    app.run(debug=True) 