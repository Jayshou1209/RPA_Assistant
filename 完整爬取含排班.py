"""
综合爬取方案 - 司机信息 + 工作排班（从路线数据提取）
生成包含完整排班信息的Excel报表
"""

from real_api_scraper import RealAPIScraper
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import json

print("=" * 70)
print("司机完整数据爬取 - 包含工作排班")
print("=" * 70)

scraper = RealAPIScraper()

# 询问模式
print("\n选择爬取模式:")
print("1. 测试模式 (前20位司机 + 今天路线)")
print("2. 完整模式 (所有司机 + 今天路线)")
print("3. 多日模式 (所有司机 + 最近7天路线)")

choice = input("\n请选择 (1-3, 默认1): ").strip() or "1"

if choice == "1":
    driver_limit = 20
    days = 1
    mode_name = "测试模式"
elif choice == "2":
    driver_limit = None
    days = 1
    mode_name = "完整模式"
else:
    driver_limit = None
    days = 7
    mode_name = "多日模式"

print(f"\n{mode_name} - 开始爬取...")
print("=" * 70)

# 1. 获取所有司机基本信息
print("\n1️⃣ 获取司机基本信息...")
print("-" * 70)

if driver_limit:
    drivers = scraper.get_all_drivers(per_page=driver_limit)
else:
    drivers = scraper.get_all_drivers(per_page=100)

print(f"✓ 获取到 {len(drivers)} 位司机")

# 2. 获取每位司机的详细信息
print("\n2️⃣ 获取司机详细信息...")
print("-" * 70)

driver_details = {}
# 测试模式只获取前10个,其他模式获取全部
detail_limit = 10 if (driver_limit and driver_limit < 50) else len(drivers)
for i, driver in enumerate(drivers[:detail_limit], 1):
    driver_id = driver.get('id')
    try:
        detail = scraper.get_driver_detail(driver_id)
        if detail:
            # 合并基本信息和详细信息
            full_info = {**driver, **detail}
            driver_details[driver_id] = full_info
        else:
            driver_details[driver_id] = driver
        
        if i % 10 == 0:
            print(f"  已处理 {i} 位司机...")
    except:
        driver_details[driver_id] = driver

print(f"✓ 获取到 {len(driver_details)} 位司机的详细信息")

# 3. 获取路线数据（多天）
print(f"\n3️⃣ 获取最近 {days} 天的路线数据...")
print("-" * 70)

all_routes = []
for day_offset in range(days):
    date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')
    print(f"  获取 {date} 的路线...")
    
    day_routes = scraper.get_all_routes(date=date, per_page=100)
    all_routes.extend(day_routes)

print(f"✓ 共获取 {len(all_routes)} 条路线")

# 4. 分析每位司机的工作排班
print("\n4️⃣ 分析司机工作排班...")
print("-" * 70)

driver_schedules = defaultdict(lambda: {
    'driver_id': None,
    'driver_name': None,
    'phone': None,
    'email': None,
    'car': None,
    'plate': None,
    'company': None,
    'total_routes': 0,
    'work_days': set(),
    'earliest_start': None,
    'latest_end': None,
    'total_hours': 0,
    'routes_by_date': defaultdict(list),
    'status_counts': defaultdict(int)
})

for route in all_routes:
    driver_id = route.get('driver_id')
    
    if driver_id and driver_id in driver_details:
        schedule = driver_schedules[driver_id]
        driver_info = driver_details[driver_id]
        
        # 填充司机基本信息
        if not schedule['driver_name']:
            schedule['driver_id'] = driver_id
            schedule['driver_name'] = f"{driver_info.get('first_name', '')} {driver_info.get('last_name', '')}"
            schedule['phone'] = driver_info.get('phone_number')
            schedule['email'] = driver_info.get('email')
            schedule['car'] = driver_info.get('title')
            schedule['plate'] = driver_info.get('plate_number')
            schedule['company'] = driver_info.get('company_name')
        
        # 统计路线
        schedule['total_routes'] += 1
        
        # 提取时间信息
        start_time = route.get('from_datetime')
        end_time = route.get('to_datetime')
        
        if start_time:
            # 记录工作日期
            work_date = start_time.split()[0] if ' ' in start_time else start_time[:10]
            schedule['work_days'].add(work_date)
            
            # 更新最早/最晚时间
            if not schedule['earliest_start'] or start_time < schedule['earliest_start']:
                schedule['earliest_start'] = start_time
        
        if end_time:
            if not schedule['latest_end'] or end_time > schedule['latest_end']:
                schedule['latest_end'] = end_time
        
        # 计算工作时长
        if start_time and end_time:
            try:
                start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                hours = (end_dt - start_dt).total_seconds() / 3600
                schedule['total_hours'] += hours
            except:
                pass
        
        # 按日期记录路线
        if start_time:
            route_info = {
                'date': work_date,
                'start': start_time,
                'end': end_time,
                'status': route.get('status'),
                'zone': route.get('starting_zone'),
            }
            schedule['routes_by_date'][work_date].append(route_info)
        
        # 统计状态
        status = route.get('status', 'unknown')
        schedule['status_counts'][status] += 1

print(f"✓ 分析了 {len(driver_schedules)} 位司机的工作排班")

# 5. 准备Excel数据
print("\n5️⃣ 准备导出数据...")
print("-" * 70)

# 司机基本信息表
basic_data = []
for driver_id, info in driver_details.items():
    basic_data.append({
        'ID': driver_id,
        '姓名': f"{info.get('first_name', '')} {info.get('last_name', '')}",
        '电话': info.get('phone_number'),
        '邮箱': info.get('email'),
        'TLC执照': info.get('tlc_license'),
        '驾照': info.get('driver_license'),
        '州': info.get('driver_license_state'),
        '车辆': info.get('title'),
        '车牌': info.get('plate_number'),
        '公司': info.get('company_name'),
        '状态': info.get('status'),
        '总行程数': info.get('total_rides', 0),
        '本周行程': info.get('total_rides_cur_week', 0),
        '上周行程': info.get('total_rides_prev_week', 0),
        '接单率': info.get('acceptance_rate', 0),
        '在线': '是' if info.get('online') else '否',
    })

# 工作排班汇总表
schedule_data = []
for driver_id, schedule in driver_schedules.items():
    schedule_data.append({
        'ID': driver_id,
        '姓名': schedule['driver_name'],
        '电话': schedule['phone'],
        '车辆': schedule['car'],
        '车牌': schedule['plate'],
        '公司': schedule['company'],
        '总路线数': schedule['total_routes'],
        '工作天数': len(schedule['work_days']),
        '工作日期': ', '.join(sorted(schedule['work_days'])),
        '最早开始': schedule['earliest_start'],
        '最晚结束': schedule['latest_end'],
        '总工时(小时)': round(schedule['total_hours'], 1),
        '已完成': schedule['status_counts'].get('finished', 0),
        '进行中': schedule['status_counts'].get('active', 0),
        '已取消': schedule['status_counts'].get('canceled', 0),
    })

# 每日排班明细表
daily_schedule_data = []
for driver_id, schedule in driver_schedules.items():
    for date, routes in schedule['routes_by_date'].items():
        for route in routes:
            daily_schedule_data.append({
                'ID': driver_id,
                '姓名': schedule['driver_name'],
                '日期': date,
                '开始时间': route['start'],
                '结束时间': route['end'],
                '状态': route['status'],
                '区域': route['zone'],
                '车辆': schedule['car'],
                '车牌': schedule['plate'],
            })

# 6. 导出Excel
print("\n6️⃣ 导出Excel...")
print("-" * 70)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
excel_file = f"data/司机完整数据_含排班_{timestamp}.xlsx"

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    # 工作排班汇总
    if schedule_data:
        df = pd.DataFrame(schedule_data)
        df = df.sort_values('总路线数', ascending=False)
        df.to_excel(writer, sheet_name='工作排班汇总', index=False)
        print(f"  ✓ 工作排班汇总: {len(schedule_data)} 行")
    
    # 每日排班明细
    if daily_schedule_data:
        df = pd.DataFrame(daily_schedule_data)
        df = df.sort_values(['日期', '开始时间'])
        df.to_excel(writer, sheet_name='每日排班明细', index=False)
        print(f"  ✓ 每日排班明细: {len(daily_schedule_data)} 行")
    
    # 司机基本信息
    if basic_data:
        df = pd.DataFrame(basic_data)
        df.to_excel(writer, sheet_name='司机基本信息', index=False)
        print(f"  ✓ 司机基本信息: {len(basic_data)} 行")
    
    # 原始路线数据
    if all_routes:
        df = pd.DataFrame(all_routes)
        df.to_excel(writer, sheet_name='原始路线数据', index=False)
        print(f"  ✓ 原始路线数据: {len(all_routes)} 行")

print(f"\n✓ Excel文件已保存: {excel_file}")

# 7. 显示统计摘要
print("\n" + "=" * 70)
print("📊 数据摘要")
print("=" * 70)
print(f"司机总数: {len(driver_details)} 位")
print(f"路线总数: {len(all_routes)} 条")
print(f"有工作记录的司机: {len(driver_schedules)} 位")
print(f"数据日期范围: {days} 天")

if driver_schedules:
    # 显示工作最多的前5位司机
    top_drivers = sorted(driver_schedules.items(), 
                        key=lambda x: x[1]['total_routes'], 
                        reverse=True)[:5]
    
    print(f"\n工作最多的前5位司机:")
    for i, (driver_id, schedule) in enumerate(top_drivers, 1):
        print(f"  {i}. {schedule['driver_name']}")
        print(f"     路线: {schedule['total_routes']} 条 | 工时: {schedule['total_hours']:.1f} 小时")

print("\n" + "=" * 70)
print("✓ 完成！")
print("=" * 70)
print(f"\n文件位置: {excel_file}")
print("\nExcel包含以下工作表:")
print("  1. 工作排班汇总 - 每位司机的排班统计")
print("  2. 每日排班明细 - 具体的工作时间安排")
print("  3. 司机基本信息 - 联系方式、车辆等")
print("  4. 原始路线数据 - 完整的路线记录")
