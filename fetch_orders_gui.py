"""
快速爬取指定订单的数据并在GUI中展示
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import sys
import os
import re

# 添加当前目录到路径  
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api_client import APIClient
import config


class OrderFetcher:
    def __init__(self, root):
        self.root = root
        self.root.title("订单数据爬取")
        self.root.geometry("900x700")
        
        # 输出文本框
        self.output = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10))
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 开始爬取
        self.log("开始爬取订单数据...\n")
        threading.Thread(target=self.fetch_orders, daemon=True).start()
    
    def log(self, message):
        """输出日志"""
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)
        self.root.update()
    
    def fetch_orders(self):
        """爬取订单"""
        api_client = APIClient(config.BEARER_TOKEN)
        order_ids = [11987090, 11976453, 12010117, 12001579, 12017243]
        
        for order_id in order_ids:
            self.log(f"\n{'='*80}")
            self.log(f"正在爬取订单: {order_id}")
            self.log('='*80)
            
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
                self.log(f"\n订单ID: {order_id}")
                self.log(f"状态: {status}")
                self.log(f"乘客: {passenger}")
                self.log(f"司机: {driver}")
                self.log(f"接客时间: {ride.get('pickup_at', ride.get('schedule_time', 'N/A'))}")
                self.log(f"接客地点: {ride.get('start_address', 'N/A')[:60]}")
                self.log(f"送达地点: {ride.get('destination_address', 'N/A')[:60]}")
                
                self.log(f"\n【账单计算】")
                self.log(f"  原始价格 (from events): ${original_price:.2f}")
                self.log(f"  Co Pay: ${co_pay:.2f}")
                if co_pay_note:
                    self.log(f"    ├─ Label: {co_pay_note['label']}")
                    self.log(f"    ├─ Description: {co_pay_note['description']}")
                    self.log(f"    └─ Icon: {co_pay_note['icon']}")
                self.log(f"  订单价格 (Original - Co Pay): ${order_price:.2f}")
                self.log(f"  TOLL费 (Vendor - Order Price): ${toll_fee:.2f}")
                self.log(f"  ─────────────────────────")
                self.log(f"  Vendor Amount (最终): ${vendor_amount:.2f}")
                self.log(f"  Driver Net (司机净收入): ${driver_net:.2f}")
                
                # 显示所有notes
                if notes:
                    self.log(f"\n【所有Notes】")
                    for i, note in enumerate(notes, 1):
                        self.log(f"  {i}. Label: {note.get('label', '')}")
                        self.log(f"     Description: {note.get('description', '')}")
                        self.log(f"     Icon: {note.get('icon', '')}")
                
                # 显示events (前3条)
                if events:
                    self.log(f"\n【Events (前3条)】")
                    for i, event in enumerate(events[:3], 1):
                        self.log(f"  {i}. {event.get('body', '')[:100]}")
                
            except Exception as e:
                self.log(f"\n✗ 爬取订单 {order_id} 失败: {e}")
                import traceback
                self.log(traceback.format_exc())
        
        self.log(f"\n\n{'='*80}")
        self.log("爬取完成！")
        self.log('='*80)


if __name__ == "__main__":
    root = tk.Tk()
    app = OrderFetcher(root)
    root.mainloop()
