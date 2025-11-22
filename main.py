"""
RPA调度系统自动化脚本 - 主程序
实现自动登录、数据爬取、派工、退工、订单转派功能
"""

import sys
import logging
from datetime import datetime
from api_client import APIClient
from scraper import DataScraper
from dispatcher import Dispatcher
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """打印欢迎横幅"""
    banner = """
    ========================================
    RPA调度系统自动化脚本
    ========================================
    功能：
    1. 自动登录调度系统
    2. 爬取司机资料、车型、开工时间段
    3. 派工功能
    4. 退工功能
    5. 订单转派功能
    ========================================
    """
    print(banner)


def print_menu():
    """打印功能菜单"""
    menu = """
    请选择功能：
    
    [数据操作]
    1. 爬取所有数据（司机、车辆、排班）
    2. 查看司机列表
    3. 查看车辆列表
    4. 查看排班信息
    
    [调度操作]
    5. 派工（单个）
    6. 批量派工
    7. 退工（单个）
    8. 批量退工
    9. 订单转派
    10. 查看司机订单
    
    [系统操作]
    11. 更新Token
    12. 测试连接
    0. 退出
    
    请输入选项: """
    return input(menu)


def scrape_data_menu(scraper: DataScraper):
    """数据爬取菜单"""
    print("\n正在爬取数据...")
    data = scraper.scrape_all_data()
    
    # 保存数据
    scraper.save_data(data)
    
    # 显示摘要
    print(f"\n数据爬取完成！")
    print(f"司机数量: {len(data.get('drivers', []))}")
    print(f"车辆数量: {len(data.get('vehicles', []))}")
    print(f"排班数量: {len(data.get('schedules', []))}")
    
    print(scraper.get_driver_summary(data.get('drivers', [])))


def view_drivers_menu(scraper: DataScraper):
    """查看司机列表"""
    drivers = scraper.get_drivers()
    print(scraper.get_driver_summary(drivers))


def dispatch_order_menu(dispatcher: Dispatcher):
    """派工菜单"""
    print("\n=== 派工 ===")
    try:
        driver_id = int(input("请输入司机ID: "))
        order_id = int(input("请输入订单ID: "))
        date = input("请输入日期 (YYYY-MM-DD，直接回车使用今天): ").strip()
        time_slot = input("请输入时间段 (例如 09:00-12:00，可选): ").strip()
        
        result = dispatcher.dispatch_order(
            driver_id=driver_id,
            order_id=order_id,
            date=date if date else None,
            time_slot=time_slot if time_slot else None
        )
        
        print(f"\n派工结果: {result}")
    except ValueError:
        print("输入错误，请输入有效的数字")
    except Exception as e:
        print(f"派工失败: {e}")


def batch_dispatch_menu(dispatcher: Dispatcher):
    """批量派工菜单"""
    print("\n=== 批量派工 ===")
    print("请输入派工信息，每行格式: 司机ID,订单ID,日期,时间段")
    print("例如: 123,456,2025-11-20,09:00-12:00")
    print("输入空行结束:")
    
    dispatch_list = []
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            parts = line.split(',')
            item = {
                'driver_id': int(parts[0]),
                'order_id': int(parts[1]),
                'date': parts[2] if len(parts) > 2 else None,
                'time_slot': parts[3] if len(parts) > 3 else None
            }
            dispatch_list.append(item)
        except Exception as e:
            print(f"格式错误: {e}，请重新输入")
    
    if dispatch_list:
        results = dispatcher.batch_dispatch(dispatch_list)
        print(f"\n批量派工完成，共处理 {len(results)} 个订单")


def withdraw_order_menu(dispatcher: Dispatcher):
    """退工菜单"""
    print("\n=== 退工 ===")
    try:
        order_id = int(input("请输入订单ID: "))
        reason = input("请输入退工原因 (可选): ").strip()
        
        result = dispatcher.withdraw_order(
            order_id=order_id,
            reason=reason if reason else None
        )
        
        print(f"\n退工结果: {result}")
    except ValueError:
        print("输入错误，请输入有效的数字")
    except Exception as e:
        print(f"退工失败: {e}")


def transfer_order_menu(dispatcher: Dispatcher):
    """订单转派菜单"""
    print("\n=== 订单转派 ===")
    try:
        order_id = int(input("请输入订单ID: "))
        from_driver_id = int(input("请输入原司机ID: "))
        to_driver_id = int(input("请输入目标司机ID: "))
        date = input("请输入日期 (YYYY-MM-DD，直接回车使用今天): ").strip()
        reason = input("请输入转派原因 (可选): ").strip()
        
        result = dispatcher.transfer_order(
            order_id=order_id,
            from_driver_id=from_driver_id,
            to_driver_id=to_driver_id,
            date=date if date else None,
            reason=reason if reason else None
        )
        
        print(f"\n转派结果: {result}")
    except ValueError:
        print("输入错误，请输入有效的数字")
    except Exception as e:
        print(f"转派失败: {e}")


def update_token_menu(api_client: APIClient):
    """更新Token菜单"""
    print("\n=== 更新Token ===")
    new_token = input("请输入新的Bearer Token: ").strip()
    
    if new_token:
        api_client.update_token(new_token)
        print("Token已更新！")
    else:
        print("Token不能为空")


def main():
    """主函数"""
    print_banner()
    
    # 初始化客户端
    logger.info("初始化API客户端...")
    api_client = APIClient()
    
    # 验证连接
    print("\n正在验证连接...")
    if api_client.verify_connection():
        print("✓ 连接成功！")
    else:
        print("✗ 连接失败，请检查Token是否有效")
        return
    
    # 初始化爬取器和调度器
    scraper = DataScraper(api_client)
    dispatcher = Dispatcher(api_client)
    
    # 主循环
    while True:
        try:
            choice = print_menu()
            
            if choice == '0':
                print("\n感谢使用，再见！")
                break
            elif choice == '1':
                scrape_data_menu(scraper)
            elif choice == '2':
                view_drivers_menu(scraper)
            elif choice == '3':
                vehicles = scraper.get_vehicles()
                print(f"\n车辆数量: {len(vehicles)}")
                for v in vehicles[:10]:
                    print(f"  - {v}")
            elif choice == '4':
                schedules = scraper.get_schedules()
                print(f"\n排班数量: {len(schedules)}")
                for s in schedules[:10]:
                    print(f"  - {s}")
            elif choice == '5':
                dispatch_order_menu(dispatcher)
            elif choice == '6':
                batch_dispatch_menu(dispatcher)
            elif choice == '7':
                withdraw_order_menu(dispatcher)
            elif choice == '8':
                order_ids_str = input("请输入订单ID列表（用逗号分隔）: ").strip()
                order_ids = [int(x.strip()) for x in order_ids_str.split(',') if x.strip()]
                reason = input("请输入退工原因 (可选): ").strip()
                results = dispatcher.batch_withdraw(order_ids, reason if reason else None)
                print(f"\n批量退工完成，共处理 {len(results)} 个订单")
            elif choice == '9':
                transfer_order_menu(dispatcher)
            elif choice == '10':
                driver_id = int(input("请输入司机ID: "))
                date = input("请输入日期 (YYYY-MM-DD，直接回车使用今天): ").strip()
                orders = dispatcher.get_driver_orders(driver_id, date if date else None)
                print(f"\n订单数量: {len(orders)}")
                for o in orders:
                    print(f"  - {o}")
            elif choice == '11':
                update_token_menu(api_client)
            elif choice == '12':
                if api_client.verify_connection():
                    print("✓ 连接正常！")
                else:
                    print("✗ 连接失败")
            else:
                print("\n无效的选项，请重新选择")
            
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n\n程序被中断")
            break
        except Exception as e:
            logger.error(f"发生错误: {e}", exc_info=True)
            print(f"\n发生错误: {e}")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()
