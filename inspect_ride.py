"""查看订单详细结构"""
from api_client import APIClient
import json

client = APIClient()

ride_id = 11677408

print(f"订单 {ride_id} 的完整结构:\n")

response = client.get(f'/rides/{ride_id}')
ride_data = response.get('ride', {})

print(json.dumps(ride_data, indent=2, ensure_ascii=False))

# 查找可能的取消或退工相关字段
print("\n\n===== 关键字段分析 =====")
print(f"status: {ride_data.get('status')}")
print(f"driver_id: {ride_data.get('driver_id')}")
print(f"driver: {ride_data.get('driver', {}).get('name') if ride_data.get('driver') else None}")

if 'actions' in ride_data:
    print(f"actions: {ride_data['actions']}")
if 'links' in ride_data:
    print(f"links: {ride_data['links']}")
if '_links' in ride_data:
    print(f"_links: {ride_data['_links']}")
