import os
from backend.app import create_app, print_startup_message

def main():
    # 获取环境配置
    env = os.getenv('FLASK_ENV', 'development')
    
    # 创建应用（这一步会自动检查数据库连接）
    app = create_app()
    
    # 打印启动信息
    print_startup_message()
    
    # 根据环境启动应用
    if env == 'development':
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
