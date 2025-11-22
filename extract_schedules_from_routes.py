"""
从路线数据中提取司机工作排班信息
"""

from real_api_scraper import RealAPIScraper
from datetime import datetime
from collections import defaultdict
import json

print("=" * 70)
print("从路线数据提取司机工作排班")
print("=" * 70)

scraper = RealAPIScraper()

# 获取今天的路线数据
today = datetime.now().strftime('%Y-%m-%d')
print(f"\n获取 {today} 的路线数据...")
print("-" * 70)

routes = scraper.get_all_routes(date=today, per_page=100)

print(f"✓ 获取到 {len(routes)} 条路线")

if routes:
    # 分析第一条路线的数据结构
    print(f"\n路线数据结构 (第一条):")
    print("-" * 70)
    sample_route = routes[0]
    
    print(f"字段列表:")
    for key in sorted(sample_route.keys()):
        value = sample_route[key]
        print(f"  {key}: {value}")
    
    # 提取司机工作统计
    print(f"\n" + "=" * 70)
    print("司机工作统计")
    print("=" * 70)
    
    driver_stats = defaultdict(lambda: {
        'driver_id': None,
        'driver_name': None,
        'total_routes': 0,
        'routes': [],
        'earliest_start': None,
        'latest_end': None,
        'statuses': defaultdict(int)
    })
    
    for route in routes:
        # 查找司机相关字段
        driver_id = None
        driver_name = None
        
        # 可能的司机ID字段
        for key in ['driver_id', 'driver', 'assigned_driver_id']:
            if key in route:
                driver_id = route[key]
                break
        
        # 可能的司机名称字段
        for key in ['driver_full_name', 'driver_name', 'assigned_driver_name']:
            if key in route:
                driver_name = route[key]
                break
        
        if driver_id or driver_name:
            key = driver_id or driver_name
            
            stats = driver_stats[key]
            stats['driver_id'] = driver_id
            stats['driver_name'] = driver_name
            stats['total_routes'] += 1
            
            # 记录路线信息
            route_info = {
                'route_id': route.get('id'),
                'status': route.get('status'),
                'requested': route.get('requested'),
                'from': route.get('from'),
                'to': route.get('to'),
            }
            
            # 提取时间信息
            for time_key in ['requested', 'start_time', 'pickup_time', 'from_datetime']:
                if time_key in route and route[time_key]:
                    route_info['start_time'] = route[time_key]
                    
                    # 更新最早/最晚时间
                    if stats['earliest_start'] is None or route[time_key] < stats['earliest_start']:
                        stats['earliest_start'] = route[time_key]
                    break
            
            for time_key in ['end_time', 'dropoff_time', 'to_datetime']:
                if time_key in route and route[time_key]:
                    route_info['end_time'] = route[time_key]
                    
                    if stats['latest_end'] is None or route[time_key] > stats['latest_end']:
                        stats['latest_end'] = route[time_key]
                    break
            
            stats['routes'].append(route_info)
            
            # 统计状态
            if 'status' in route:
                stats['statuses'][route['status']] += 1
    
    # 显示统计结果
    print(f"\n共有 {len(driver_stats)} 位司机有路线记录\n")
    
    # 按路线数量排序
    sorted_drivers = sorted(driver_stats.items(), key=lambda x: x[1]['total_routes'], reverse=True)
    
    print(f"前10位司机的工作情况:")
    print("-" * 70)
    
    for i, (key, stats) in enumerate(sorted_drivers[:10], 1):
        print(f"\n{i}. {stats['driver_name'] or '未知'} (ID: {stats['driver_id'] or key})")
        print(f"   总路线: {stats['total_routes']} 条")
        print(f"   工作时间: {stats['earliest_start'] or 'N/A'} ~ {stats['latest_end'] or 'N/A'}")
        print(f"   状态分布: ", end="")
        for status, count in stats['statuses'].items():
            print(f"{status}({count}) ", end="")
        print()
    
    # 导出为Excel
    print(f"\n" + "=" * 70)
    print("导出司机工作排班数据")
    print("=" * 70)
    
    # 准备导出数据
    schedule_data = []
    for key, stats in sorted_drivers:
        schedule_data.append({
            '司机ID': stats['driver_id'],
            '司机姓名': stats['driver_name'],
            '总路线数': stats['total_routes'],
            '最早开始': stats['earliest_start'],
            '最晚结束': stats['latest_end'],
            **{f'状态_{status}': count for status, count in stats['statuses'].items()}
        })
    
    try:
        import pandas as pd
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_file = f"data/driver_schedules_{today}_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 工作排班汇总
            df_schedule = pd.DataFrame(schedule_data)
            df_schedule.to_excel(writer, sheet_name='司机工作排班', index=False)
            
            # 原始路线数据
            df_routes = pd.DataFrame(routes)
            df_routes.to_excel(writer, sheet_name='路线明细', index=False)
        
        print(f"✓ 已导出到: {excel_file}")
        
    except Exception as e:
        print(f"✗ 导出失败: {e}")

else:
    print("\n没有路线数据")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)
