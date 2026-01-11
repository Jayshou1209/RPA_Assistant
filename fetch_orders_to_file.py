"""
爬取指定订单数据并保存到文本文件
"""

import sys
import os
import re
from datetime import datetime

# 添加当前目录到路径  
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api_client import APIClient
import config


def fetch_and_save_orders():
    """爬取订单并保存到文件"""
    api_client = APIClient(config.BEARER_TOKEN)
    order_ids = [11987090, 11976453, 12010117, 12001579, 12017243]
    
    # 创建输出文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(current_dir, f'订单数据_{timestamp}.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        def log(message):
            print(message)
            f.write(message + '\n')
            f.flush()
        
        log("="*80)
        log("开始爬取订单数据")
        log("="*80)
        
        for order_id in order_ids:
            log(f"\n{'='*80}")
            log(f"正在爬取订单: {order_id}")
            log('='*80)
            
            try:
                # 获取订单详情
                detail = api_client.get(f'/fleet/rides/{order_id}')
                ride = detail.get('ride', {})
                
                # 基本信息
                status = ride.get('status', '')
                passenger = f"{ride.get('first_name', '')} {ride.get('last_name', '')}".strip()
                driver = f"{ride.get('driver_first_name', '')} {ride.get('driver_last_name', '')}".strip()
                
                # 价格信息
                vendor_amount = float(ride.get('vendor_amount', 0) or 0)
                driver_net = float(ride.get('driver_net', 0) or 0)
                
                # 从events中提取原始订单价格
                events = ride.get('events', [])
                original_price = 0
                for event in events:
                    body = event.get('body', '')
                    match = re.search(r'reserved.*for\s+\$([0-9]+\.?[0-9]*)', body, re.IGNORECASE)
                    if match:
                        original_price = float(match.group(1))
                        break
                
                # 提取Co Pay信息
                notes = ride.get('notes', [])
                co_pay = 0
                co_pay_note = None
                
                for note in notes:
                    label = note.get('label', '')
                    description = note.get('description', '').lower()
                    icon = note.get('icon', '')
                    
                    # 查找Co Pay金额
                    match = re.search(r'\$([0-9]+\.?[0-9]*)', label)
                    if match:
                        if icon == 'private' or 'collect' in description or 'cash' in description:
                            co_pay = float(match.group(1))
                            co_pay_note = {
                                'label': label,
                                'description': description,
                                'icon': icon
                            }
                            break
                
                # 计算账单金额 - 按照gui.py中的逻辑
                if status in ['no_show', 'driver_canceled']:
                    order_price = 5.0
                    co_pay = 0
                    toll_fee = 0
                    original_price = 5.0
                else:
                    # finished订单的正常计算
                    if original_price == 0:
                        # 没有events说明vendor_amount就是最终价格，无TOLL信息
                        order_price = round(vendor_amount - co_pay, 2)
                        toll_fee = 0
                        original_price = vendor_amount
                    else:
                        # 有events说明有原始价格，可以计算TOLL
                        # 订单价格 = 原始价格 - co_pay
                        # TOLL = vendor_amount - 订单价格
                        order_price = round(original_price - co_pay, 2)
                        toll_fee = round(vendor_amount - order_price, 2)
                
                # 显示订单信息
                log(f"\n订单ID: {order_id}")
                log(f"状态: {status}")
                log(f"乘客: {passenger}")
                log(f"司机: {driver}")
                log(f"接客时间: {ride.get('pickup_at', ride.get('schedule_time', 'N/A'))}")
                log(f"接客地点: {ride.get('start_address', 'N/A')}")
                log(f"送达地点: {ride.get('destination_address', 'N/A')}")
                
                log(f"\n【账单计算 - 按照gui.py的逻辑】")
                log(f"  原始价格 (from events): ${original_price:.2f}")
                log(f"  Co Pay: ${co_pay:.2f}")
                if co_pay_note:
                    log(f"    ├─ Label: {co_pay_note['label']}")
                    log(f"    ├─ Description: {co_pay_note['description']}")
                    log(f"    └─ Icon: {co_pay_note['icon']}")
                log(f"  订单价格 (Original - Co Pay): ${order_price:.2f}")
                log(f"  TOLL费 (Vendor - Order Price): ${toll_fee:.2f}")
                log(f"  ─────────────────────────")
                log(f"  Vendor Amount (最终金额): ${vendor_amount:.2f}")
                log(f"  Driver Net (司机净收入): ${driver_net:.2f}")
                
                # 显示所有notes
                if notes:
                    log(f"\n【所有Notes】")
                    for i, note in enumerate(notes, 1):
                        log(f"  {i}. Label: {note.get('label', '')}")
                        log(f"     Description: {note.get('description', '')}")
                        log(f"     Icon: {note.get('icon', '')}")
                
                # 显示events (前5条)
                if events:
                    log(f"\n【Events (前5条)】")
                    for i, event in enumerate(events[:5], 1):
                        log(f"  {i}. {event.get('body', '')}")
                
            except Exception as e:
                log(f"\n✗ 爬取订单 {order_id} 失败: {e}")
                import traceback
                log(traceback.format_exc())
        
        log(f"\n\n{'='*80}")
        log("爬取完成！")
        log(f"结果已保存到: {output_file}")
        log('='*80)
    
    print(f"\n文件已保存到: {output_file}")
    return output_file


if __name__ == "__main__":
    try:
        output_file = fetch_and_save_orders()
        print(f"\n✓ 完成！请查看文件: {output_file}")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按Enter键退出...")
