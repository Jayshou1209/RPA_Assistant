"""
配置文件示例 - 复制此文件为 config.py 并填入实际的Token
"""

# API配置
API_BASE_URL = "http://api-admin.myle.tech/api/v1"

# Token配置 - 每天更新
# 最后更新时间: YYYY-MM-DD
BEARER_TOKEN = "Bearer YOUR_TOKEN_HERE"

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间(秒)
MAX_RETRIES = 3  # 最大重试次数

# 数据存储配置
DATA_DIR = "data"  # 数据存储目录
DRIVER_DATA_FILE = "driver_data.json"  # 司机数据文件
LOG_FILE = "automation.log"  # 日志文件

# 调度系统端点
ENDPOINTS = {
    "login": "/auth/verify",
    "drivers": "/drivers",
    "vehicles": "/vehicles", 
    "schedules": "/schedules",
    "dispatch": "/dispatch",
    "withdraw": "/withdraw",
    "transfer": "/transfer"
}
