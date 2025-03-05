"""
全局配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# Flask应用配置
class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'

    # 数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123456'  # 请修改为你的实际密码
    MYSQL_DB = 'chart_renter'
    MYSQL_PORT = 3308

    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 3600  # 24小时

CRAWLER_CONFIG = {
    'target_urls': [
        'https://wuhan.zu.fang.com/house/i31/',  # 武汉租房总列表页
    ],
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
}

# 爬虫配置

# 文件路径配置
PATH_CONFIG = {
    'raw_data': 'data/raw/wuhan_housing.csv',  # 原始数据
    'log_dir': 'data/logs'  # 日志目录
}

# 确保所有路径都是相对于项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for key in PATH_CONFIG:
    PATH_CONFIG[key] = os.path.join(PROJECT_ROOT, PATH_CONFIG[key])
