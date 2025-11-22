"""
自动化示例脚本 - 演示如何编程方式使用RPA模块
"""

from api_client import APIClient
from scraper import DataScraper
from dispatcher import Dispatcher
import config
from datetime import datetime, timedelta


def example_daily_data_sync():
    """示例1: 每日数据同步"""
    print("=" * 60)
    print("示例1: 每日数据同步")
    print("=" * 60)
    
    # 初始化客户端
    client = APIClient()
    scraper = DataScraper(client)
    
    # 爬取数据
    print("\n正在爬取数据...")
    data = scraper.scrape_all_data()
    
    # 保存数据
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"data_backup_{today}.json"
    scraper.save_data(data, filename)
    
    print(f"\n✓ 数据已保存到: data/{filename}")
    print(f"  - 司机数量: {len(data['drivers'])}")
    print(f"  - 车辆数量: {len(data['vehicles'])}")
    print(f"  - 排班数量: {len(data['schedules'])}")


def example_auto_dispatch():
    """示例2: 自动派工"""
    print("\n" + "=" * 60)
    print("示例2: 自动派工")
    print("=" * 60)
    
    client = APIClient()
    dispatcher = Dispatcher(client)
    
    # 批量派工数据
    dispatch_list = [
        {
            'driver_id': 123,
            'order_id': 1001,
            'date': '2025-11-20',
            'time_slot': '09:00-12:00'
        },
        {
            'driver_id': 124,
            'order_id': 1002,
            'date': '2025-11-20',
            'time_slot': '13:00-17:00'
        },
        {
            'driver_id': 125,
            'order_id': 1003,
            'date': '2025-11-20',
            'time_slot': '18:00-22:00'
        }
    ]
    
    print(f"\n准备派工 {len(dispatch_list)} 个订单...")
    results = dispatcher.batch_dispatch(dispatch_list)
    
    # 统计结果
    success_count = sum(1 for r in results if r['result'].get('success'))
    print(f"\n✓ 派工完成: {success_count}/{len(results)} 成功")


def example_driver_schedule_check():
    """示例3: 检查司机排班"""
    print("\n" + "=" * 60)
    print("示例3: 检查司机排班")
    print("=" * 60)
    
    client = APIClient()
    scraper = DataScraper(client)
    dispatcher = Dispatcher(client)
    
    # 获取所有司机
    drivers = scraper.get_drivers()
    print(f"\n找到 {len(drivers)} 位司机")
    
    # 检查今天的订单
    today = datetime.now().strftime('%Y-%m-%d')
    
    for driver in drivers[:5]:  # 只检查前5位司机
        driver_id = driver.get('id')
        driver_name = driver.get('name', '未知')
        
        orders = dispatcher.get_driver_orders(driver_id, today)
        print(f"\n司机 {driver_name} (ID: {driver_id}): {len(orders)} 个订单")
        
        for order in orders:
            print(f"  - 订单 {order.get('order_id')}: {order.get('time_slot')}")


def example_order_transfer():
    """示例4: 订单转派（司机临时不可用）"""
    print("\n" + "=" * 60)
    print("示例4: 订单转派")
    print("=" * 60)
    
    client = APIClient()
    dispatcher = Dispatcher(client)
    
    # 场景：司机123临时请假，将订单转给司机124
    from_driver_id = 123
    to_driver_id = 124
    order_id = 1001
    
    print(f"\n将订单 {order_id} 从司机 {from_driver_id} 转给司机 {to_driver_id}")
    
    result = dispatcher.transfer_order(
        order_id=order_id,
        from_driver_id=from_driver_id,
        to_driver_id=to_driver_id,
        reason="司机临时请假"
    )
    
    if result.get('success'):
        print("✓ 转派成功")
    else:
        print(f"✗ 转派失败: {result.get('error')}")


def example_batch_withdraw():
    """示例5: 批量退工"""
    print("\n" + "=" * 60)
    print("示例5: 批量退工")
    print("=" * 60)
    
    client = APIClient()
    dispatcher = Dispatcher(client)
    
    # 需要退工的订单列表
    order_ids = [1001, 1002, 1003]
    
    print(f"\n准备退工 {len(order_ids)} 个订单...")
    results = dispatcher.batch_withdraw(order_ids, reason="批量调整")
    
    success_count = sum(1 for r in results if r['result'].get('success'))
    print(f"\n✓ 退工完成: {success_count}/{len(results)} 成功")


def example_smart_dispatch():
    """示例6: 智能派工（根据司机状态和空闲时间）"""
    print("\n" + "=" * 60)
    print("示例6: 智能派工")
    print("=" * 60)
    
    client = APIClient()
    scraper = DataScraper(client)
    dispatcher = Dispatcher(client)
    
    # 获取可用司机
    drivers = scraper.get_drivers({'status': 'active'})
    print(f"\n找到 {len(drivers)} 位可用司机")
    
    # 获取今天的排班
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 查找空闲司机
    available_drivers = []
    for driver in drivers:
        orders = dispatcher.get_driver_orders(driver['id'], today)
        if len(orders) < 3:  # 假设每位司机最多3个订单
            available_drivers.append({
                'id': driver['id'],
                'name': driver.get('name'),
                'current_orders': len(orders)
            })
    
    print(f"\n空闲司机 ({len(available_drivers)} 位):")
    for d in available_drivers[:5]:
        print(f"  - {d['name']} (ID: {d['id']}): {d['current_orders']} 个订单")
    
    # 自动分配新订单给空闲司机
    if available_drivers:
        new_order_id = 2001
        selected_driver = available_drivers[0]
        
        print(f"\n将新订单 {new_order_id} 分配给司机 {selected_driver['name']}")
        result = dispatcher.dispatch_order(
            driver_id=selected_driver['id'],
            order_id=new_order_id,
            date=today,
            time_slot='09:00-12:00'
        )
        
        if result.get('success'):
            print("✓ 智能派工成功")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("RPA自动化脚本示例集")
    print("=" * 60)
    
    examples = [
        ("每日数据同步", example_daily_data_sync),
        ("自动派工", example_auto_dispatch),
        ("检查司机排班", example_driver_schedule_check),
        ("订单转派", example_order_transfer),
        ("批量退工", example_batch_withdraw),
        ("智能派工", example_smart_dispatch)
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. 运行所有示例")
    
    choice = input("\n请选择要运行的示例 (0-6): ").strip()
    
    try:
        if choice == '0':
            # 运行所有示例
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n✗ {name} 失败: {e}")
                input("\n按回车继续下一个示例...")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("无效的选择")
    except ValueError:
        print("请输入有效的数字")
    except KeyboardInterrupt:
        print("\n\n程序被中断")
    except Exception as e:
        print(f"\n发生错误: {e}")


if __name__ == "__main__":
    main()
