"""
配置文件 - 存储API配置和Token
"""

# API配置 - 正确的API端点
API_BASE_URL = "https://api-admin.myle.tech/api/v1/fleet"

# Token配置 - 每天更新
# 最后更新时间: 2025-11-22
BEARER_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vYXBpLWFkbWluLm15bGUudGVjaC9hcGkvdjEvYXV0aC92ZXJpZnkiLCJpYXQiOjE3NjM3OTkyMzIsImV4cCI6MTc2Mzg4NTYzMiwibmJmIjoxNzYzNzk5MjMyLCJqdGkiOiJjenBRbmp4S2hURkp3eUVJIiwic3ViIjoiODUwIiwicHJ2IjoiYTIzYjU3M2RjNzNhNDA3ZThkZTUzYjQ4NmYzNjg4NmFkZjcwYzQ4MyIsImZpbiI6IjQ4OTAwMTEyYzAzNDM5NzY2N2E4MmVjZjA1MzRhMjhmIiwiY29tcGFuaWVzIjpbbnVsbF0sImZ1bGxfYWNjZXNzIjowLCJmbGVldF9pZCI6MzQsInR5cGUiOiJhZG1pbiJ9.xsweCAyYLXI4iWVMiSS5x7IPD-cGBbs55ES-Ju7l-lw"

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间(秒)
MAX_RETRIES = 3  # 最大重试次数

# 数据存储配置
DATA_DIR = "data"  # 数据存储目录
DRIVER_DATA_FILE = "driver_data.json"  # 司机数据文件
LOG_FILE = "automation.log"  # 日志文件

# 调度系统端点（支持分页）
ENDPOINTS = {
    "login": "/auth/verify",
    "drivers": "/drivers",  # 参数: page, per_page, search, sort_by, sort_by_type
    "vehicles": "/vehicles", 
    "cars": "/fleets/34/cars",
    "schedules": "/schedules",
    "routes": "/routes",  # 参数: page, per_page, statuses, from_datetime, to_datetime
    "bookings": "/bookings",
    "trips": "/trips",
    "dispatch": "/dispatch",
    "withdraw": "/withdraw",
    "transfer": "/transfer",
    "user": "/user",
    "me": "/me"
}
