"""
爬取指定订单的数据
"""

import sys
import os
import re

# 添加当前目录到路径  
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api_client import APIClient
import config

def fetch_order_details(order_ids):
    """爬取指定订单的详细数据"""
    api_client = APIClient(config.BEARER_TOKEN)
    
    results = []
    
    for order_id in order_ids:
        print(f"\n{'='*60}")
        print(f"正在爬取订单: {order_id}")
        print('='*60)
        
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
            
            # 计算账单金额
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
            print(f"\n订单ID: {order_id}")
            print(f"状态: {status}")
            print(f"乘客: {passenger}")
            print(f"司机: {driver}")
            print(f"接客时间: {ride.get('pickup_at', ride.get('schedule_time', 'N/A'))}")
            print(f"接客地点: {ride.get('start_address', 'N/A')}")
            print(f"送达地点: {ride.get('destination_address', 'N/A')}")
            print(f"\n--- 价格详情 ---")
            print(f"原始价格 (Original Price from events): ${original_price:.2f}")
            print(f"Co Pay: ${co_pay:.2f}")
            if co_pay_note:
                print(f"  来源: {co_pay_note['label']}")
                print(f"  描述: {co_pay_note['description']}")
                print(f"  图标: {co_pay_note['icon']}")
            print(f"订单价格 (Order Price = Original Price - Co Pay): ${order_price:.2f}")
            print(f"TOLL费 (Toll = Vendor Amount - Order Price): ${toll_fee:.2f}")
            print(f"Vendor Amount (最终金额): ${vendor_amount:.2f}")
            print(f"Driver Net (司机净收入): ${driver_net:.2f}")
            
            # 显示所有notes
            if notes:
                print(f"\n--- 所有Notes ---")
                for i, note in enumerate(notes, 1):
                    print(f"{i}. Label: {note.get('label', '')}")
                    print(f"   Description: {note.get('description', '')}")
                    print(f"   Icon: {note.get('icon', '')}")
            
            # 显示所有events
            if events:
                print(f"\n--- 所有Events (前5条) ---")
                for i, event in enumerate(events[:5], 1):
                    print(f"{i}. {event.get('body', '')}")
            
            results.append({
                'order_id': order_id,
                'status': status,
                'passenger': passenger,
                'driver': driver,
                'vendor_amount': vendor_amount,
                'driver_net': driver_net,
                'original_price': original_price,
                'co_pay': co_pay,
                'order_price': order_price,
                'toll_fee': toll_fee,
                'pickup_at': ride.get('pickup_at', ride.get('schedule_time', '')),
                'start_address': ride.get('start_address', ''),
                'destination_address': ride.get('destination_address', ''),
                'notes': notes,
                'events': events
            })
            
        except Exception as e:
            print(f"\n✗ 爬取订单 {order_id} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    return results


if __name__ == "__main__":
    # 要爬取的订单ID列表
    order_ids = [11987090, 11976453, 12010117, 12001579, 12017243]
    
    print("="*60)
    print("开始爬取订单数据")
    print("="*60)
    
    results = fetch_order_details(order_ids)
    
    print("\n\n")
    print("="*60)
    print("爬取完成！")
    print("="*60)
    print(f"成功爬取 {len(results)} 个订单")
