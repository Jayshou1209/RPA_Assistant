"""
完整数据爬取脚本 - 爬取所有司机和路线数据并导出Excel
"""

from real_api_scraper import RealAPIScraper
from datetime import datetime
import sys

def main():
    print("=" * 70)
    print("Myle Dashboard 完整数据爬取")
    print("=" * 70)
    
    scraper = RealAPIScraper()
    
    # 询问用户选项
    print("\n请选择爬取模式:")
    print("1. 快速测试 (前50条司机 + 今天的路线)")
    print("2. 完整爬取 (所有司机 + 今天的路线)")
    print("3. 仅司机数据")
    print("4. 仅路线数据")
    
    choice = input("\n请输入选项 (1-4，默认1): ").strip() or "1"
    
    print("\n" + "=" * 70)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'drivers': [],
        'routes': [],
        'metadata': {}
    }
    
    # 爬取司机数据
    if choice in ["1", "2", "3"]:
        print("\n📊 开始爬取司机数据...")
        print("-" * 70)
        
        if choice == "1":
            # 测试模式 - 前50条
            result['drivers'] = scraper.get_all_drivers(per_page=50)
        else:
            # 完整模式 - 所有数据
            result['drivers'] = scraper.get_all_drivers(per_page=100)
        
        result['metadata']['total_drivers'] = len(result['drivers'])
        print(f"\n✓ 司机数据爬取完成: {len(result['drivers'])} 位")
    
    # 爬取路线数据
    if choice in ["1", "2", "4"]:
        print("\n🚗 开始爬取路线数据...")
        print("-" * 70)
        
        # 询问日期
        date_input = input("\n请输入日期 (YYYY-MM-DD，默认今天): ").strip()
        target_date = date_input if date_input else datetime.now().strftime('%Y-%m-%d')
        
        if choice == "1":
            # 测试模式 - 前50条
            result['routes'] = scraper.get_all_routes(date=target_date, per_page=50)
        else:
            # 完整模式 - 所有数据
            result['routes'] = scraper.get_all_routes(date=target_date, per_page=100)
        
        result['metadata']['total_routes'] = len(result['routes'])
        result['metadata']['route_date'] = target_date
        print(f"\n✓ 路线数据爬取完成: {len(result['routes'])} 条")
    
    # 数据摘要
    print("\n" + "=" * 70)
    print("📋 数据摘要")
    print("=" * 70)
    print(f"司机总数: {result['metadata'].get('total_drivers', 0)}")
    print(f"路线总数: {result['metadata'].get('total_routes', 0)}")
    print(f"路线日期: {result['metadata'].get('route_date', 'N/A')}")
    
    # 保存数据
    print("\n" + "=" * 70)
    print("💾 保存数据")
    print("=" * 70)
    
    # 保存JSON
    json_file = scraper.save_to_json(result)
    print(f"✓ JSON: {json_file}")
    
    # 导出Excel
    try:
        excel_file = scraper.export_to_excel(result)
        print(f"✓ Excel: {excel_file}")
    except Exception as e:
        print(f"✗ Excel导出失败: {e}")
        print("提示: 请确保已安装 pandas 和 openpyxl")
        print("安装命令: pip install pandas openpyxl")
    
    print("\n" + "=" * 70)
    print("✓ 完成！")
    print("=" * 70)
    
    # 显示数据样例
    if result['drivers']:
        print(f"\n司机数据样例 (前3位):")
        for i, d in enumerate(result['drivers'][:3], 1):
            print(f"\n{i}. {d.get('first_name')} {d.get('last_name')}")
            print(f"   ID: {d.get('id')}")
            print(f"   电话: {d.get('phone_number')}")
            print(f"   邮箱: {d.get('email')}")
            print(f"   TLC执照: {d.get('tlc_license')}")
            print(f"   驾照: {d.get('driver_license')} ({d.get('driver_license_state')})")
            print(f"   车辆: {d.get('title')} - {d.get('plate_number')}")
            print(f"   公司: {d.get('company_name')}")
            print(f"   状态: {d.get('status')}")
            print(f"   总行程: {d.get('total_rides')}")
            print(f"   在线: {'是' if d.get('online') else '否'}")
    
    if result['routes']:
        print(f"\n\n路线数据样例 (前3条):")
        for i, r in enumerate(result['routes'][:3], 1):
            print(f"\n{i}. 路线 #{r.get('id')}")
            # 根据实际返回的字段调整
            for key in ['driver_full_name', 'car', 'status', 'requested', 'from', 'to']:
                if key in r:
                    print(f"   {key}: {r[key]}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
