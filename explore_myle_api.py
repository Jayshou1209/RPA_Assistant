"""
Myle Tech API探测器 - 基于Dashboard URL找到正确的API端点
"""

import requests
import json

# 使用你提供的Token
TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vYXBpLWFkbWluLm15bGUudGVjaC9hcGkvdjEvYXV0aC92ZXJpZnkiLCJpYXQiOjE3NjM2MjYxNDcsImV4cCI6MTc2MzcxMjU0NywibmJmIjoxNzYzNjI2MTQ3LCJqdGkiOiIycGJCeno0UXFHdE44MGJkIiwic3ViIjoiODUwIiwicHJ2IjoiYTIzYjU3M2RjNzNhNDA3ZThkZTUzYjQ4NmYzNjg4NmFkZjcwYzQ4MyIsImZpbiI6IjQ4OTAwMTEyYzAzNDM5NzY2N2E4MmVjZjA1MzRhMjhmIiwiY29tcGFuaWVzIjpbbnVsbF0sImZ1bGxfYWNjZXNzIjowLCJmbGVldF9pZCI6MzQsInR5cGUiOiJhZG1pbiJ9.tbh_i-pgagfwnlUSOZajJjW_Y6rlf9A6Te_o03M-bkY"

# 可能的API基础URL
BASE_URLS = [
    "https://api-admin.myle.tech/api/v1",
    "https://api.myle.tech/api/v1",
    "https://dashboard.myle.tech/api/v1",
]

headers = {
    'Authorization': TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

print("=" * 70)
print("Myle Tech API探测器")
print("=" * 70)
print(f"\nToken (前50字符): {TOKEN[:50]}...")
print(f"Dashboard: https://dashboard.myle.tech")
print("\n" + "=" * 70)

# 从Token中解析fleet_id
import base64
try:
    token_parts = TOKEN.split('.')[1]
    # 添加padding
    token_parts += '=' * (4 - len(token_parts) % 4)
    decoded = base64.b64decode(token_parts)
    token_data = json.loads(decoded)
    fleet_id = token_data.get('fleet_id')
    user_id = token_data.get('sub')
    print(f"\nToken信息:")
    print(f"  Fleet ID: {fleet_id}")
    print(f"  User ID: {user_id}")
    print(f"  Type: {token_data.get('type')}")
    print(f"  Full Access: {token_data.get('full_access')}")
except Exception as e:
    print(f"\n解析Token失败: {e}")
    fleet_id = 34

print("\n" + "=" * 70)

# 测试端点（基于fleet_id）
test_endpoints = [
    # 司机相关
    f"/fleets/{fleet_id}/drivers",
    f"/fleet/{fleet_id}/drivers", 
    "/drivers",
    f"/fleets/{fleet_id}/members",
    
    # 车辆相关
    f"/fleets/{fleet_id}/vehicles",
    f"/fleet/{fleet_id}/vehicles",
    "/vehicles",
    f"/fleets/{fleet_id}/cars",
    
    # 订单/行程相关
    f"/fleets/{fleet_id}/bookings",
    f"/fleets/{fleet_id}/trips",
    f"/fleets/{fleet_id}/orders",
    "/bookings",
    "/trips",
    
    # 排班相关
    f"/fleets/{fleet_id}/schedules",
    f"/fleets/{fleet_id}/shifts",
    "/schedules",
    
    # 用户信息
    "/user",
    "/me",
    f"/users/{user_id}",
]

successful = []
forbidden = []
not_found = []

print("\n开始探测API端点...\n")

for base_url in BASE_URLS:
    print(f"\n测试基础URL: {base_url}")
    print("-" * 70)
    
    for endpoint in test_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            status = response.status_code
            
            if status == 200:
                print(f"✓ [200 OK]          {endpoint}")
                try:
                    data = response.json()
                    # 显示返回的数据结构
                    if isinstance(data, dict):
                        if 'data' in data:
                            data_content = data['data']
                            if isinstance(data_content, list):
                                print(f"    └─ 返回列表，共 {len(data_content)} 项")
                                if data_content:
                                    print(f"    └─ 示例数据键: {list(data_content[0].keys())[:5]}")
                            else:
                                print(f"    └─ 返回数据键: {list(data.keys())}")
                        else:
                            print(f"    └─ 返回键: {list(data.keys())[:5]}")
                except:
                    pass
                successful.append((base_url, endpoint, response))
                
            elif status == 403:
                print(f"✗ [403 Forbidden]   {endpoint}")
                forbidden.append((base_url, endpoint))
                
            elif status == 404:
                print(f"  [404 Not Found]   {endpoint}")
                not_found.append((base_url, endpoint))
                
            elif status == 401:
                print(f"✗ [401 Unauthorized] {endpoint}")
                
            elif status == 405:
                print(f"  [405 Method Not Allowed] {endpoint}")
                
            else:
                print(f"  [{status}]           {endpoint}")
                
        except requests.exceptions.Timeout:
            print(f"⏱ [Timeout]         {endpoint}")
        except requests.exceptions.ConnectionError:
            print(f"✗ [Connection Error] {endpoint}")
        except Exception as e:
            pass

print("\n" + "=" * 70)
print("探测结果汇总")
print("=" * 70)

if successful:
    print(f"\n✓ 成功访问的端点 ({len(successful)}个):\n")
    
    current_base = None
    for base_url, endpoint, response in successful:
        if base_url != current_base:
            print(f"\n  Base URL: {base_url}")
            current_base = base_url
        print(f"  ├─ {endpoint}")
        
        # 显示数据样例
        try:
            data = response.json()
            if 'data' in data and isinstance(data['data'], list) and data['data']:
                sample = data['data'][0]
                print(f"  │  └─ 数据样例: {json.dumps(sample, ensure_ascii=False)[:100]}...")
        except:
            pass
    
    print("\n" + "=" * 70)
    print("推荐配置:")
    print("=" * 70)
    
    # 找到最常用的base_url
    base_url_counts = {}
    for base_url, _, _ in successful:
        base_url_counts[base_url] = base_url_counts.get(base_url, 0) + 1
    
    best_base_url = max(base_url_counts.items(), key=lambda x: x[1])[0]
    
    print(f"\n在 config.py 中更新:")
    print(f'\nAPI_BASE_URL = "{best_base_url}"')
    
    print("\nENDPOINTS = {")
    
    # 整理端点
    endpoint_map = {}
    for base_url, endpoint, _ in successful:
        if base_url == best_base_url:
            if 'driver' in endpoint.lower():
                endpoint_map['drivers'] = endpoint
            elif 'vehicle' in endpoint.lower() or 'car' in endpoint.lower():
                endpoint_map['vehicles'] = endpoint
            elif 'booking' in endpoint.lower():
                endpoint_map['bookings'] = endpoint
            elif 'trip' in endpoint.lower():
                endpoint_map['trips'] = endpoint
            elif 'schedule' in endpoint.lower() or 'shift' in endpoint.lower():
                endpoint_map['schedules'] = endpoint
    
    for key, endpoint in endpoint_map.items():
        print(f'    "{key}": "{endpoint}",')
    
    print("}")
    
else:
    print("\n✗ 没有找到可访问的端点")
    print("\n可能的原因:")
    print("1. Token已过期")
    print("2. API结构与预期不同")
    print("3. 需要特殊的认证流程")

if forbidden:
    print(f"\n⚠️  权限不足的端点 ({len(forbidden)}个):")
    print("这些端点存在但Token无权访问")

print("\n" + "=" * 70)
