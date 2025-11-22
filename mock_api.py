"""
测试模式 - 使用模拟数据测试GUI功能
当API无法访问时，使用此模式测试界面
"""

import json
import os
from datetime import datetime

# 模拟司机数据
MOCK_DRIVERS = [
    {"id": 101, "name": "张三", "phone": "13800138001", "status": "active", "vehicle_type": "轿车"},
    {"id": 102, "name": "李四", "phone": "13800138002", "status": "active", "vehicle_type": "SUV"},
    {"id": 103, "name": "王五", "phone": "13800138003", "status": "active", "vehicle_type": "面包车"},
    {"id": 104, "name": "赵六", "phone": "13800138004", "status": "inactive", "vehicle_type": "轿车"},
    {"id": 105, "name": "钱七", "phone": "13800138005", "status": "active", "vehicle_type": "货车"},
]

# 模拟车辆数据
MOCK_VEHICLES = [
    {"id": 201, "plate": "京A12345", "type": "轿车", "model": "丰田凯美瑞", "status": "available", "driver_id": 101},
    {"id": 202, "plate": "京B67890", "type": "SUV", "model": "本田CRV", "status": "available", "driver_id": 102},
    {"id": 203, "plate": "京C11111", "type": "面包车", "model": "五菱宏光", "status": "available", "driver_id": 103},
    {"id": 204, "plate": "京D22222", "type": "轿车", "model": "大众帕萨特", "status": "maintenance", "driver_id": 104},
]

# 模拟排班数据
MOCK_SCHEDULES = [
    {"id": 301, "driver_id": 101, "driver_name": "张三", "date": "2025-11-20", "time_slot": "09:00-12:00", "status": "scheduled", "order_id": 1001},
    {"id": 302, "driver_id": 102, "driver_name": "李四", "date": "2025-11-20", "time_slot": "13:00-17:00", "status": "scheduled", "order_id": 1002},
    {"id": 303, "driver_id": 103, "driver_name": "王五", "date": "2025-11-20", "time_slot": "18:00-22:00", "status": "scheduled", "order_id": 1003},
]


class MockAPIClient:
    """模拟API客户端 - 用于测试"""
    
    def __init__(self, token=None):
        self.token = token
        self.base_url = "http://api-admin.myle.tech/api/v1"
        print("⚠️ 警告: 使用模拟数据模式（API无法访问）")
    
    def verify_connection(self):
        """模拟连接验证"""
        print("✓ 模拟连接成功（使用测试数据）")
        return True
    
    def get(self, endpoint, params=None):
        """模拟GET请求"""
        if 'drivers' in endpoint:
            return {'success': True, 'data': MOCK_DRIVERS}
        elif 'vehicles' in endpoint or 'cars' in endpoint:
            return {'success': True, 'data': MOCK_VEHICLES}
        elif 'schedules' in endpoint:
            return {'success': True, 'data': MOCK_SCHEDULES}
        else:
            return {'success': True, 'data': []}
    
    def post(self, endpoint, json_data=None, data=None):
        """模拟POST请求"""
        print(f"模拟POST请求: {endpoint}")
        print(f"数据: {json_data}")
        return {'success': True, 'message': '操作成功（模拟）'}
    
    def update_token(self, new_token):
        """更新Token"""
        self.token = new_token
        print("✓ Token已更新（模拟模式）")


class MockDataScraper:
    """模拟数据爬取器"""
    
    def __init__(self, api_client):
        self.api = api_client
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_drivers(self, params=None):
        """获取司机数据"""
        return MOCK_DRIVERS
    
    def get_vehicles(self, params=None):
        """获取车辆数据"""
        return MOCK_VEHICLES
    
    def get_schedules(self, params=None):
        """获取排班数据"""
        return MOCK_SCHEDULES
    
    def scrape_all_data(self):
        """爬取所有数据"""
        return {
            'timestamp': datetime.now().isoformat(),
            'drivers': MOCK_DRIVERS,
            'vehicles': MOCK_VEHICLES,
            'schedules': MOCK_SCHEDULES,
            'mode': 'mock'
        }
    
    def save_data(self, data, filename='driver_data.json'):
        """保存数据"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 数据已保存到: {filepath}")
    
    def load_data(self, filename='driver_data.json'):
        """加载数据"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None


class MockDispatcher:
    """模拟调度器"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def dispatch_order(self, driver_id, order_id, date=None, time_slot=None, **kwargs):
        """模拟派工"""
        print(f"模拟派工: 司机{driver_id} → 订单{order_id}")
        return {
            'success': True,
            'message': f'订单{order_id}已分配给司机{driver_id}（模拟）'
        }
    
    def withdraw_order(self, order_id, driver_id=None, reason=None, **kwargs):
        """模拟退工"""
        print(f"模拟退工: 订单{order_id}")
        return {
            'success': True,
            'message': f'订单{order_id}已取消分配（模拟）'
        }
    
    def transfer_order(self, order_id, from_driver_id, to_driver_id, date=None, reason=None, **kwargs):
        """模拟转派"""
        print(f"模拟转派: 订单{order_id} 从司机{from_driver_id} → 司机{to_driver_id}")
        return {
            'success': True,
            'message': f'订单已从司机{from_driver_id}转给司机{to_driver_id}（模拟）'
        }
    
    def batch_dispatch(self, dispatch_list):
        """模拟批量派工"""
        results = []
        for item in dispatch_list:
            result = self.dispatch_order(
                driver_id=item.get('driver_id'),
                order_id=item.get('order_id'),
                date=item.get('date'),
                time_slot=item.get('time_slot')
            )
            results.append({
                'order_id': item.get('order_id'),
                'driver_id': item.get('driver_id'),
                'result': result
            })
        return results
    
    def batch_withdraw(self, order_ids, reason=None):
        """模拟批量退工"""
        results = []
        for order_id in order_ids:
            result = self.withdraw_order(order_id=order_id, reason=reason)
            results.append({
                'order_id': order_id,
                'result': result
            })
        return results
    
    def get_driver_orders(self, driver_id, date=None):
        """模拟获取司机订单"""
        return [s for s in MOCK_SCHEDULES if s['driver_id'] == driver_id]


# 使用说明
if __name__ == "__main__":
    print("=" * 60)
    print("测试模式启动")
    print("=" * 60)
    print("\n这是一个使用模拟数据的测试模式")
    print("用于在API无法访问时测试GUI功能\n")
    
    # 创建模拟对象
    client = MockAPIClient()
    scraper = MockDataScraper(client)
    dispatcher = MockDispatcher(client)
    
    # 测试功能
    print("\n测试数据爬取:")
    data = scraper.scrape_all_data()
    print(f"✓ 司机: {len(data['drivers'])} 位")
    print(f"✓ 车辆: {len(data['vehicles'])} 辆")
    print(f"✓ 排班: {len(data['schedules'])} 条")
    
    print("\n测试派工:")
    result = dispatcher.dispatch_order(101, 2001)
    print(f"✓ {result['message']}")
    
    print("\n=" * 60)
    print("测试模式可以正常使用！")
    print("=" * 60)
    print("\n要启动GUI测试模式，运行:")
    print("python gui_test_mode.py")
