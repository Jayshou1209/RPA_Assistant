"""
完整爬取司机数据 - 包括详细信息和所有可能的排班数据
"""

from real_api_scraper import RealAPIScraper
import json
from datetime import datetime

print("=" * 70)
print("完整爬取司机详细数据（包括排班信息）")
print("=" * 70)

scraper = RealAPIScraper()

# 获取前5位司机测试
print("\n获取前5位司机的完整信息...")
print("-" * 70)

# 1. 先获取司机列表
params = {'page': 1, 'per_page': 5}
response = scraper.api.get('/drivers', params=params)

if isinstance(response, dict):
    drivers_data = response.get('drivers', {})
    if isinstance(drivers_data, dict):
        drivers_list = drivers_data.get('data', [])
        
        print(f"获取到 {len(drivers_list)} 位司机\n")
        
        # 2. 获取每位司机的详细信息
        detailed_drivers = []
        
        for i, driver in enumerate(drivers_list, 1):
            driver_id = driver.get('id')
            driver_name = f"{driver.get('first_name')} {driver.get('last_name')}"
            
            print(f"{i}. {driver_name} (ID: {driver_id})")
            print("-" * 70)
            
            try:
                # 获取司机详情
                detail_response = scraper.api.get(f'/drivers/{driver_id}')
                
                if isinstance(detail_response, dict):
                    # 合并基本信息和详细信息
                    full_data = {**driver}
                    
                    # 添加所有详情字段
                    for key in ['driver', 'company', 'documents', 'payment_methods', 'cars', 'ratings', 'balance', 'transactions']:
                        if key in detail_response:
                            if key == 'driver':
                                # 合并driver字段到主数据
                                if isinstance(detail_response[key], dict):
                                    full_data.update(detail_response[key])
                            else:
                                # 其他字段作为子对象
                                full_data[key] = detail_response[key]
                    
                    detailed_drivers.append(full_data)
                    
                    # 显示该司机的所有字段
                    print("所有可用字段:")
                    all_keys = set(full_data.keys())
                    for key in sorted(all_keys):
                        value = full_data[key]
                        if isinstance(value, (dict, list)):
                            print(f"  {key}: {type(value).__name__} (长度: {len(value) if value else 0})")
                        else:
                            print(f"  {key}: {value}")
                    
                    # 特别关注排班相关字段
                    schedule_keywords = ['schedule', 'shift', 'availability', 'working', 'hours', 'time']
                    found_schedule_fields = [k for k in all_keys if any(kw in k.lower() for kw in schedule_keywords)]
                    
                    if found_schedule_fields:
                        print(f"\n  ⚠️ 发现可能的排班字段: {found_schedule_fields}")
                        for field in found_schedule_fields:
                            print(f"    {field} = {full_data[field]}")
                    else:
                        print(f"\n  ℹ️ 未找到排班相关字段")
                    
                    print()
                    
            except Exception as e:
                print(f"  ✗ 获取详情失败: {e}\n")
                detailed_drivers.append(driver)
        
        # 3. 检查是否有其他相关的API端点
        print("\n" + "=" * 70)
        print("尝试查找排班数据的其他可能端点")
        print("=" * 70)
        
        # 尝试不同的URL模式
        test_endpoints = [
            # 全局排班端点
            ('/driver-schedules', {}),
            ('/work-schedules', {}),
            ('/shifts', {}),
            
            # 特定司机的排班
            (f'/drivers/{drivers_list[0]["id"]}/schedule', {}),
            (f'/drivers/{drivers_list[0]["id"]}/schedules', {}),
            (f'/drivers/{drivers_list[0]["id"]}/shifts', {}),
            (f'/drivers/{drivers_list[0]["id"]}/availability', {}),
            (f'/drivers/{drivers_list[0]["id"]}/working-hours', {}),
            
            # 带日期参数的查询
            ('/schedules', {'date': datetime.now().strftime('%Y-%m-%d')}),
            ('/shifts', {'driver_id': drivers_list[0]["id"]}),
        ]
        
        found_endpoints = []
        
        for endpoint, params in test_endpoints:
            try:
                result = scraper.api.get(endpoint, params=params)
                
                # 如果成功返回且有数据
                if isinstance(result, dict):
                    has_data = False
                    for key in result.keys():
                        if isinstance(result[key], (list, dict)) and result[key]:
                            has_data = True
                            break
                    
                    if has_data:
                        print(f"✓ {endpoint} - 找到数据!")
                        print(f"  返回键: {list(result.keys())[:5]}")
                        found_endpoints.append((endpoint, params, result))
                        
            except Exception as e:
                error_msg = str(e)
                if '404' not in error_msg and '403' not in error_msg:
                    print(f"  {endpoint} - {error_msg[:60]}")
        
        # 4. 导出数据
        print("\n" + "=" * 70)
        print("导出完整数据")
        print("=" * 70)
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'drivers_detailed': detailed_drivers,
            'schedule_endpoints_found': [{'endpoint': ep, 'params': params} for ep, params, _ in found_endpoints],
            'metadata': {
                'total_drivers': len(detailed_drivers),
                'fields_per_driver': len(detailed_drivers[0].keys()) if detailed_drivers else 0
            }
        }
        
        # 保存JSON
        json_file = f"data/drivers_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON: {json_file}")
        
        # 导出Excel
        try:
            import pandas as pd
            
            excel_file = f"data/drivers_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # 司机基本信息
                if detailed_drivers:
                    # 展平数据以便Excel显示
                    flat_drivers = []
                    for driver in detailed_drivers:
                        flat = {}
                        for key, value in driver.items():
                            if isinstance(value, (dict, list)):
                                # 复杂对象转为JSON字符串
                                flat[key] = json.dumps(value, ensure_ascii=False)
                            else:
                                flat[key] = value
                        flat_drivers.append(flat)
                    
                    df = pd.DataFrame(flat_drivers)
                    df.to_excel(writer, sheet_name='司机完整信息', index=False)
                
                # 如果找到了排班数据
                if found_endpoints:
                    for i, (endpoint, params, data) in enumerate(found_endpoints, 1):
                        sheet_name = f'排班数据{i}'[:31]
                        # 尝试提取列表数据
                        for key, value in data.items():
                            if isinstance(value, list) and value:
                                df = pd.DataFrame(value)
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                break
            
            print(f"✓ Excel: {excel_file}")
            
        except Exception as e:
            print(f"✗ Excel导出失败: {e}")
        
        print("\n" + "=" * 70)
        print("总结")
        print("=" * 70)
        print(f"共获取 {len(detailed_drivers)} 位司机的完整信息")
        print(f"每位司机包含 {export_data['metadata']['fields_per_driver']} 个字段")
        
        if found_endpoints:
            print(f"\n找到 {len(found_endpoints)} 个排班相关端点:")
            for endpoint, params, _ in found_endpoints:
                print(f"  - {endpoint}")
        else:
            print("\n⚠️ 未找到独立的排班数据端点")
            print("\n可能的原因:")
            print("1. 排班数据可能在其他模块/页面")
            print("2. 排班数据可能需要特殊权限")
            print("3. 排班数据可能通过前端计算（从routes生成）")
            print("\n建议:")
            print("- 在浏览器中打开司机详情页，查看Network请求")
            print("- 或使用之前的extract_schedules_from_routes.py从路线数据提取")

print("\n" + "=" * 70)
