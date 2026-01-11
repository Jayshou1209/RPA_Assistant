"""
RPA调度系统 - 调度管理工具
专注于派工、转派、退工功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import re
from datetime import datetime, timedelta
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
from api_client import APIClient
from dispatcher import Dispatcher
import config
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)


class DispatchManagerGUI:
    """调度管理工具GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RPA调度管理工具 v1.0")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 初始化变量
        self.api_client = None
        self.dispatcher = None
        self.real_scraper = None
        self.token_var = tk.StringVar(value=config.BEARER_TOKEN)
        self.status_var = tk.StringVar(value="就绪")
        
        # 后台监控线程控制
        self.auto_withdraw_running = False
        self.auto_withdraw_thread = None
        
        # 保存上次的司机ID和退工时间
        self.last_driver_ids = ""
        self.last_withdraw_minutes = "90"
        self.settings_file = os.path.join(config.DATA_DIR, "dispatcher_settings.json")
        self._load_settings()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化API客户端
        self.initialize_client()
    
    def _load_settings(self):
        """从文件加载上次的设置"""
        try:
            if os.path.exists(self.settings_file):
                import json
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.last_driver_ids = settings.get('driver_ids', '')
                    self.last_withdraw_minutes = settings.get('withdraw_minutes', '90')
                    logger.info(f"已加载上次的设置: 司机ID={self.last_driver_ids}, 退工时间={self.last_withdraw_minutes}")
        except Exception as e:
            logger.warning(f"加载设置失败: {e}")
    
    def _save_settings(self):
        """保存当前设置到文件"""
        try:
            import json
            settings = {
                'driver_ids': self.last_driver_ids,
                'withdraw_minutes': self.last_withdraw_minutes
            }
            # 确保目录存在
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存设置到 {self.settings_file}")
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 1. 功能按钮区域
        self.create_function_buttons(main_frame)
        
        # 2. 输出显示区域
        self.create_output_section(main_frame)
        
        # 3. 状态栏
        self.create_status_bar(main_frame)
    
    def create_token_section(self, parent):
        """创建Token管理区域"""
        token_frame = ttk.LabelFrame(parent, text="📝 Token管理", padding="10")
        token_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Token输入
        ttk.Label(token_frame, text="Bearer Token:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        token_entry = ttk.Entry(token_frame, textvariable=self.token_var, width=80)
        token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # 按钮组
        btn_frame = ttk.Frame(token_frame)
        btn_frame.grid(row=0, column=2, padx=(5, 0))
        
        ttk.Button(btn_frame, text="💾 保存Token", command=self.save_token).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 重新加载", command=self.reload_token).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✓ 测试连接", command=self.test_connection).pack(side=tk.LEFT, padx=2)
        
        token_frame.columnconfigure(1, weight=1)
    
    def create_function_buttons(self, parent):
        """创建功能按钮区域"""
        # 左侧按钮面板
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=(0, 10))
        
        # 调度操作
        dispatch_frame = ttk.LabelFrame(btn_frame, text="🎯 调度操作", padding="10")
        dispatch_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(dispatch_frame, text="➕ 派工 (Assign)", command=self.show_dispatch_dialog, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(dispatch_frame, text="🔄 转派 (Switch)", command=self.show_transfer_dialog, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(dispatch_frame, text="➖ 退工 (Revive)", command=self.show_withdraw_dialog, width=25).pack(fill=tk.X, pady=2)
        
        # 高级功能
        advanced_frame = ttk.LabelFrame(btn_frame, text="⚡ 高级功能", padding="10")
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(advanced_frame, text="💰 高价订单筛选", command=self.show_high_price_filter_dialog, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(advanced_frame, text="⏰ 实时退工监控", command=self.show_auto_withdraw_dialog, width=25).pack(fill=tk.X, pady=2)
        
        # 查询功能
        query_frame = ttk.LabelFrame(btn_frame, text="🔍 查询功能", padding="10")
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(query_frame, text="📋 查看司机订单", command=self.show_driver_orders_dialog, width=25).pack(fill=tk.X, pady=2)
        
        # 系统操作
        system_frame = ttk.LabelFrame(btn_frame, text="⚙️ 系统", padding="10")
        system_frame.pack(fill=tk.X)
        
        ttk.Button(system_frame, text="📜 查看日志文件", command=self.view_logs, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(system_frame, text="🗑️ 清空输出", command=self.clear_output, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(system_frame, text="ℹ️ 关于", command=self.show_about, width=25).pack(fill=tk.X, pady=2)
    
    def create_output_section(self, parent):
        """创建输出显示区域"""
        output_frame = ttk.LabelFrame(parent, text="📺 输出信息", padding="10")
        output_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建带滚动条的文本框
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=30,
            font=("Consolas", 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签样式
        self.output_text.tag_config("success", foreground="green", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("error", foreground="red", font=("Consolas", 10, "bold"))
        self.output_text.tag_config("info", foreground="blue")
        self.output_text.tag_config("warning", foreground="orange")
        
        self.log("=" * 60)
        self.log("欢迎使用 RPA调度管理工具", "info")
        self.log("=" * 60)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT)
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        status_label.pack(side=tk.LEFT, padx=5)
        
        # 添加时间显示
        self.time_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ttk.Label(status_frame, textvariable=self.time_var).pack(side=tk.RIGHT)
        self.update_time()
    
    def update_time(self):
        """更新时间显示"""
        self.time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    def log(self, message, tag=""):
        """输出日志"""
        self.output_text.insert(tk.END, f"{message}\n", tag)
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def set_status(self, status):
        """设置状态"""
        self.status_var.set(status)
        self.root.update_idletasks()
    
    def initialize_client(self):
        """初始化API客户端"""
        try:
            from real_api_scraper import RealAPIScraper
            self.api_client = APIClient(self.token_var.get())
            self.dispatcher = Dispatcher(self.api_client)
            self.real_scraper = RealAPIScraper(self.api_client)
            self.log("✓ API客户端初始化成功", "success")
        except Exception as e:
            self.log(f"✗ 初始化失败: {str(e)}", "error")
            logger.error(f"初始化失败: {e}", exc_info=True)
    
    # ==================== Token管理 ====================
    
    def save_token(self):
        """保存Token"""
        try:
            new_token = self.token_var.get().strip()
            if not new_token:
                messagebox.showerror("错误", "Token不能为空")
                return
            
            # 保存到文件
            with open("token.txt", 'w', encoding='utf-8') as f:
                f.write(new_token)
            
            # 更新API客户端
            self.api_client.update_token(new_token)
            
            self.log("✓ Token已保存并更新", "success")
            messagebox.showinfo("成功", "Token已保存")
        except Exception as e:
            self.log(f"✗ 保存Token失败: {str(e)}", "error")
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def reload_token(self):
        """重新加载Token"""
        try:
            with open("token.txt", 'r', encoding='utf-8-sig') as f:
                token = f.read().strip()
            self.token_var.set(token)
            self.api_client.update_token(token)
            self.log("✓ Token已重新加载", "success")
        except Exception as e:
            self.log(f"✗ 加载Token失败: {str(e)}", "error")
            messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def test_connection(self):
        """测试API连接"""
        def test():
            try:
                self.set_status("正在测试连接...")
                self.log("开始测试API连接...")
                
                # 使用verify_connection方法
                success, message = self.api_client.verify_connection()
                
                if success:
                    self.log("✓ API连接测试成功", "success")
                    self.log(f"  {message}", "info")
                    self.set_status("连接正常")
                    messagebox.showinfo("成功", f"API连接正常\n\n{message}")
                else:
                    self.log("✗ 连接测试失败", "error")
                    self.log(f"  {message}", "error")
                    self.set_status("连接失败")
                    messagebox.showerror("失败", f"连接失败\n\n{message}")
            except Exception as e:
                self.log(f"✗ 连接测试出错: {str(e)}", "error")
                self.set_status("连接出错")
                messagebox.showerror("错误", f"测试出错: {str(e)}")
        
        threading.Thread(target=test, daemon=True).start()
    
    # ==================== 调度操作 ====================
    
    def show_dispatch_dialog(self):
        """显示派工对话框 (Assign Driver)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("派工 (Assign)")
        dialog.geometry("450x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"450x200+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入字段
        ttk.Label(frame, text="订单ID (Ride ID):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=10)
        ride_id_entry = ttk.Entry(frame, width=30)
        ride_id_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Label(frame, text="司机ID (Driver ID):", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=10)
        driver_id_entry = ttk.Entry(frame, width=30)
        driver_id_entry.grid(row=1, column=1, pady=10, padx=10)
        
        def submit():
            try:
                ride_id = int(ride_id_entry.get().strip())
                driver_id = int(driver_id_entry.get().strip())
                
                self.log("=" * 60)
                self.log(f"开始派工: 订单 {ride_id} -> 司机 {driver_id}", "info")
                
                result = self.dispatcher.assign_driver(ride_id, driver_id)
                
                self.log(f"✓ 派工成功", "success")
                self.log(f"响应: {result}")
                self.log("=" * 60)
                
                messagebox.showinfo("成功", f"派工成功！\n\n订单ID: {ride_id}\n司机ID: {driver_id}")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字ID")
            except Exception as e:
                self.log(f"✗ 派工失败: {e}", "error")
                messagebox.showerror("错误", f"派工失败:\n{e}")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="确认派工", command=submit).pack(side=tk.LEFT, padx=5)
    
    def show_withdraw_dialog(self):
        """显示退工对话框 (Revive - Cancel Ride) - 按司机ID和时间段"""
        dialog = tk.Toplevel(self.root)
        dialog.title("退工 (Revive)")
        dialog.geometry("500x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"500x250+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="司机ID (Driver ID):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        driver_id_entry = ttk.Entry(frame, width=30)
        driver_id_entry.grid(row=0, column=1, pady=8, padx=10)
        
        ttk.Label(frame, text="日期 (Date):", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        date_entry = ttk.Entry(frame, width=30)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.grid(row=1, column=1, pady=8, padx=10)
        
        ttk.Label(frame, text="时间段 (Time Range):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        time_entry = ttk.Entry(frame, width=30)
        time_entry.insert(0, "00:00-23:59")
        time_entry.grid(row=2, column=1, pady=8, padx=10)
        
        ttk.Label(frame, text="取消原因:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        reason_label = ttk.Label(frame, text="Driver Cancel (固定)", foreground="gray")
        reason_label.grid(row=3, column=1, pady=8, padx=10, sticky=tk.W)
        
        def submit():
            try:
                driver_id = int(driver_id_entry.get().strip())
                date = date_entry.get().strip()
                time_range = time_entry.get().strip()
                reason = "Driver Cancel"
                
                self.log("=" * 60)
                self.log(f"开始批量退工", "info")
                self.log(f"司机ID: {driver_id}", "info")
                self.log(f"日期: {date}", "info")
                self.log(f"时间段: {time_range}", "info")
                self.log(f"原因: {reason}", "info")
                
                # 获取该司机在指定时间段的所有订单
                from_time, to_time = time_range.split('-')
                from_datetime = f"{date} {from_time.strip()}:00"
                to_datetime = f"{date} {to_time.strip()}:00"
                
                self.log(f"获取时间段: {from_datetime} ~ {to_datetime}", "info")
                
                rides = self.real_scraper.get_all_rides(
                    date=date,
                    per_page=500,
                    statuses=''
                )
                
                # 筛选该司机在指定时间段的订单
                driver_rides = []
                for r in rides:
                    if r.get('driver_id') == driver_id:
                        pickup_time = r.get('pickup_at', '')
                        if pickup_time:
                            if from_datetime[:16] <= pickup_time[:16] <= to_datetime[:16]:
                                driver_rides.append(r)
                        else:
                            driver_rides.append(r)
                
                self.log(f"找到 {len(driver_rides)} 条该司机在指定时间段的订单", "info")
                
                if len(driver_rides) == 0:
                    messagebox.showwarning("提示", f"未找到司机 {driver_id} 在该时间段的订单")
                    return
                
                # 逐个退工
                success_count = 0
                fail_count = 0
                
                for ride in driver_rides:
                    ride_id = ride.get('id')
                    status = ride.get('status', '')
                    pickup_at = ride.get('pickup_at', '')
                    
                    self.log(f"  订单 {ride_id} ({pickup_at}, 状态: {status})", "info")
                    
                    try:
                        self.dispatcher.cancel_ride(ride_id, reason)
                        success_count += 1
                        self.log(f"    ✓ 退工成功", "success")
                    except Exception as e:
                        fail_count += 1
                        error_msg = str(e)
                        if "404" in error_msg:
                            self.log(f"    ✗ 失败: 订单不允许退工 (404)", "error")
                        elif "403" in error_msg:
                            self.log(f"    ✗ 失败: 无权限 (403)", "error")
                        else:
                            self.log(f"    ✗ 失败: {e}", "error")
                
                self.log("=" * 60)
                self.log(f"✓ 批量退工完成", "success")
                self.log(f"成功: {success_count} 条, 失败: {fail_count} 条", "info")
                self.log("=" * 60)
                
                msg = f"批量退工完成！\n\n成功: {success_count} 条\n失败: {fail_count} 条"
                
                if success_count == 0 and fail_count > 0:
                    messagebox.showwarning("完成", msg + "\n\n⚠️ 所有订单退工失败\n可能原因：订单状态不允许退工")
                else:
                    messagebox.showinfo("完成", msg)
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的司机ID")
            except Exception as e:
                self.log(f"✗ 批量退工失败: {e}", "error")
                messagebox.showerror("错误", f"批量退工失败:\n{e}")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="确认批量退工", command=submit).pack(side=tk.LEFT, padx=5)
    
    def show_transfer_dialog(self):
        """显示转派对话框 (Switch Driver) - 按司机ID和时间段"""
        dialog = tk.Toplevel(self.root)
        dialog.title("转派 (Switch)")
        dialog.geometry("500x280")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (280 // 2)
        dialog.geometry(f"500x280+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="原司机ID (From Driver):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        from_driver_entry = ttk.Entry(frame, width=30)
        from_driver_entry.grid(row=0, column=1, pady=8, padx=10)
        
        ttk.Label(frame, text="新司机ID (To Driver):", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        to_driver_entry = ttk.Entry(frame, width=30)
        to_driver_entry.grid(row=1, column=1, pady=8, padx=10)
        
        ttk.Label(frame, text="日期 (Date):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        date_entry = ttk.Entry(frame, width=30)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.grid(row=2, column=1, pady=8, padx=10)
        
        ttk.Label(frame, text="时间段 (Time Range):", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        time_entry = ttk.Entry(frame, width=30)
        time_entry.insert(0, "00:00-23:59")
        time_entry.grid(row=3, column=1, pady=8, padx=10)
        
        def submit():
            try:
                from_driver_id = int(from_driver_entry.get().strip())
                to_driver_id = int(to_driver_entry.get().strip())
                date = date_entry.get().strip()
                time_range = time_entry.get().strip()
                
                self.log("=" * 60)
                self.log(f"开始批量转派", "info")
                self.log(f"原司机ID: {from_driver_id}", "info")
                self.log(f"新司机ID: {to_driver_id}", "info")
                self.log(f"日期: {date}", "info")
                self.log(f"时间段: {time_range}", "info")
                
                # 获取该司机在指定时间段的所有订单
                from_time, to_time = time_range.split('-')
                from_datetime = f"{date} {from_time.strip()}:00"
                to_datetime = f"{date} {to_time.strip()}:00"
                
                self.log(f"获取时间段: {from_datetime} ~ {to_datetime}", "info")
                
                rides = self.real_scraper.get_all_rides(
                    date=date,
                    per_page=500,
                    statuses=''
                )
                
                # 筛选该司机在指定时间段的订单
                driver_rides = []
                for r in rides:
                    if r.get('driver_id') == from_driver_id:
                        pickup_time = r.get('pickup_at', '')
                        if pickup_time:
                            if from_datetime[:16] <= pickup_time[:16] <= to_datetime[:16]:
                                driver_rides.append(r)
                        else:
                            driver_rides.append(r)
                
                self.log(f"找到 {len(driver_rides)} 条该司机在指定时间段的订单", "info")
                
                if len(driver_rides) == 0:
                    messagebox.showwarning("提示", f"未找到司机 {from_driver_id} 在该时间段的订单")
                    return
                
                # 逐个转派
                success_count = 0
                fail_count = 0
                for ride in driver_rides:
                    try:
                        ride_id = ride.get('id')
                        self.dispatcher.transfer_driver(ride_id, to_driver_id)
                        success_count += 1
                        self.log(f"  ✓ 订单 {ride_id} 转派成功", "success")
                    except Exception as e:
                        fail_count += 1
                        self.log(f"  ✗ 订单 {ride.get('id')} 转派失败: {e}", "error")
                
                self.log("=" * 60)
                self.log(f"✓ 批量转派完成", "success")
                self.log(f"成功: {success_count} 条, 失败: {fail_count} 条", "info")
                self.log("=" * 60)
                
                messagebox.showinfo("完成", f"批量转派完成！\n\n成功: {success_count} 条\n失败: {fail_count} 条")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字ID")
            except Exception as e:
                self.log(f"✗ 批量转派失败: {e}", "error")
                messagebox.showerror("错误", f"批量转派失败:\n{e}")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="确认批量转派", command=submit).pack(side=tk.LEFT, padx=5)
    
    def show_driver_orders_dialog(self):
        """查看司机订单对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("查看司机订单")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="司机ID:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=10)
        driver_id_entry = ttk.Entry(frame, width=30)
        driver_id_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Label(frame, text="日期:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=10)
        date_entry = ttk.Entry(frame, width=30)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.grid(row=1, column=1, pady=10, padx=10)
        
        def submit():
            try:
                driver_id = int(driver_id_entry.get().strip())
                date = date_entry.get().strip()
                
                self.log("=" * 60)
                self.log(f"查询司机 {driver_id} 在 {date} 的订单", "info")
                
                rides = self.real_scraper.get_all_rides(
                    date=date,
                    per_page=500,
                    statuses=''
                )
                
                driver_rides = [r for r in rides if r.get('driver_id') == driver_id]
                
                self.log(f"\n找到 {len(driver_rides)} 条订单:", "success")
                for ride in driver_rides:
                    self.log(f"  订单ID: {ride.get('id')} | 时间: {ride.get('pickup_at')} | 状态: {ride.get('status')}", "info")
                
                self.log("=" * 60)
                
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的司机ID")
            except Exception as e:
                self.log(f"✗ 查询失败: {e}", "error")
                messagebox.showerror("错误", f"查询失败: {e}")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="查询", command=submit).pack(side=tk.LEFT, padx=5)
    
    # ==================== 系统功能 ====================
    
    def view_logs(self):
        """查看日志"""
        try:
            if os.path.exists(config.LOG_FILE):
                os.startfile(config.LOG_FILE)
            else:
                messagebox.showwarning("警告", "日志文件不存在")
        except Exception as e:
            messagebox.showerror("错误", f"打开日志失败: {str(e)}")
    
    def clear_output(self):
        """清空输出"""
        self.output_text.delete(1.0, tk.END)
        self.log("=" * 60)
        self.log("输出已清空", "info")
        self.log("=" * 60)
    
    def show_about(self):
        """显示关于"""
        about_text = """
RPA调度管理工具 v1.0

专注于调度操作功能

功能：
• 派工 (Assign) - 将订单分配给司机
• 转派 (Switch) - 将订单转给其他司机
• 退工 (Revive) - 取消订单
• 查询司机订单
• 高价订单筛选 - 自动筛选并分配高价订单
• 实时退工监控 - 自动监控并退工订单

技术支持：请联系管理员
        """
        messagebox.showinfo("关于", about_text)
    
    # ==================== 高级功能 ====================
    
    def show_high_price_filter_dialog(self):
        """显示高价订单筛选对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("💰 高价订单筛选")
        dialog.geometry("550x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"550x400+{x}+{y}")
        
        # 说明
        ttk.Label(dialog, text="筛选pending状态的订单，将高于指定价格的订单分配到目标司机", 
                 wraplength=500).pack(pady=15)
        
        # 输入区域
        input_frame = ttk.Frame(dialog)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # 日期选择
        ttk.Label(input_frame, text="日期:").grid(row=0, column=0, sticky=tk.W, pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(input_frame, textvariable=date_var, width=20)
        date_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Label(input_frame, text="(格式: YYYY-MM-DD)", font=("Arial", 8)).grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # 开始时间选择
        ttk.Label(input_frame, text="开始时间:").grid(row=1, column=0, sticky=tk.W, pady=5)
        time_start_frame = ttk.Frame(input_frame)
        time_start_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        
        start_hour_var = tk.StringVar(value="09")
        start_minute_var = tk.StringVar(value="00")
        
        start_hour_combo = ttk.Combobox(time_start_frame, textvariable=start_hour_var, width=5, state='readonly')
        start_hour_combo['values'] = [f"{h:02d}" for h in range(24)]
        start_hour_combo.pack(side=tk.LEFT)
        
        ttk.Label(time_start_frame, text=":").pack(side=tk.LEFT, padx=2)
        
        start_minute_combo = ttk.Combobox(time_start_frame, textvariable=start_minute_var, width=5, state='readonly')
        start_minute_combo['values'] = ['00', '30']
        start_minute_combo.pack(side=tk.LEFT)
        
        # 结束时间选择
        ttk.Label(input_frame, text="结束时间:").grid(row=2, column=0, sticky=tk.W, pady=5)
        time_end_frame = ttk.Frame(input_frame)
        time_end_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        
        end_hour_var = tk.StringVar(value="17")
        end_minute_var = tk.StringVar(value="00")
        
        end_hour_combo = ttk.Combobox(time_end_frame, textvariable=end_hour_var, width=5, state='readonly')
        end_hour_combo['values'] = [f"{h:02d}" for h in range(24)]
        end_hour_combo.pack(side=tk.LEFT)
        
        ttk.Label(time_end_frame, text=":").pack(side=tk.LEFT, padx=2)
        
        end_minute_combo = ttk.Combobox(time_end_frame, textvariable=end_minute_var, width=5, state='readonly')
        end_minute_combo['values'] = ['00', '30']
        end_minute_combo.pack(side=tk.LEFT)
        
        # 价格限定
        ttk.Label(input_frame, text="最低价格 ($):").grid(row=3, column=0, sticky=tk.W, pady=5)
        price_var = tk.StringVar()
        price_entry = ttk.Entry(input_frame, textvariable=price_var, width=20)
        price_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 目标司机ID
        ttk.Label(input_frame, text="目标司机ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        driver_var = tk.StringVar()
        driver_entry = ttk.Entry(input_frame, textvariable=driver_var, width=20)
        driver_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        input_frame.columnconfigure(1, weight=1)
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def execute_filter():
            date = date_var.get().strip()
            start_hour = start_hour_var.get()
            start_minute = start_minute_var.get()
            end_hour = end_hour_var.get()
            end_minute = end_minute_var.get()
            price = price_var.get().strip()
            driver_id = driver_var.get().strip()
            
            if not price or not driver_id or not date:
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            try:
                min_price = float(price)
            except ValueError:
                messagebox.showerror("错误", "价格必须是数字")
                return
            
            # 验证日期格式
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("错误", "日期格式错误，请使用 YYYY-MM-DD")
                return
            
            # 构建时间字符串
            start_time = f"{start_hour}:{start_minute}"
            end_time = f"{end_hour}:{end_minute}"
            
            dialog.destroy()
            self.filter_high_price_orders(min_price, driver_id, date, start_time, end_time)
        
        ttk.Button(btn_frame, text="开始筛选", command=execute_filter, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def filter_high_price_orders(self, min_price, target_driver_id, date, start_time, end_time):
        """筛选并分配高价订单"""
        def task():
            try:
                self.set_status("正在筛选高价订单...")
                self.log(f"\n{'='*60}")
                self.log(f"开始筛选高价订单", "info")
                self.log(f"日期: {date}")
                self.log(f"时间段: {start_time} - {end_time}")
                self.log(f"价格限定: ${min_price:.2f}")
                self.log(f"目标司机ID: {target_driver_id}")
                
                # 获取pending订单
                self.log("\n获取pending订单...", "info")
                
                from real_api_scraper import RealAPIScraper
                if not self.real_scraper:
                    self.real_scraper = RealAPIScraper(self.api_client)
                
                # 获取指定日期的订单
                all_rides = self.real_scraper.get_all_rides(date=date, per_page=500, statuses='pending')
                
                self.log(f"✓ 获取到 {len(all_rides)} 个pending订单", "success")
                
                if len(all_rides) == 0:
                    self.log("\n没有找到订单", "warning")
                    self.set_status("就绪")
                    return
                
                # 解析时间范围
                start_hour, start_minute = map(int, start_time.split(':'))
                end_hour, end_minute = map(int, end_time.split(':'))
                start_minutes = start_hour * 60 + start_minute
                end_minutes = end_hour * 60 + end_minute
                
                # 第一步：筛选时间段内的订单
                self.log(f"\n第一步：筛选时间段 {start_time}-{end_time} 内的订单...", "info")
                time_matched_rides = []
                
                for ride in all_rides:
                    try:
                        ride_id = ride.get('id')
                        pickup_at = ride.get('pickup_at', '')
                        
                        if not pickup_at:
                            continue
                        
                        # 解析pickup时间
                        try:
                            if 'T' in pickup_at:
                                pickup_time = datetime.fromisoformat(pickup_at.replace('Z', '+00:00'))
                                # 转换为纽约时间（美东时间）
                                ny_tz = pytz.timezone('America/New_York')
                                pickup_time = pickup_time.astimezone(ny_tz)
                            else:
                                pickup_time = datetime.strptime(pickup_at, '%Y-%m-%d %H:%M:%S')
                            
                            # 提取小时和分钟
                            pickup_minutes = pickup_time.hour * 60 + pickup_time.minute
                            pickup_time_str = f"{pickup_time.hour:02d}:{pickup_time.minute:02d}"
                            
                            # 检查是否在时间范围内
                            if start_minutes <= pickup_minutes <= end_minutes:
                                time_matched_rides.append({
                                    'id': ride_id,
                                    'pickup_time': pickup_time_str,
                                    'pickup_at': pickup_at
                                })
                        except Exception as e:
                            continue
                    except Exception as e:
                        continue
                
                self.log(f"✓ 找到 {len(time_matched_rides)} 个时间段内的订单", "success")
                
                if len(time_matched_rides) == 0:
                    self.log("\n没有符合时间段的订单", "warning")
                    self.set_status("就绪")
                    return
                
                # 第二步：获取详细信息并筛选高价订单（多线程并发）
                self.log(f"\n第二步：获取订单详细信息并筛选价格 ≥ ${min_price:.2f} 的订单...", "info")
                self.log(f"  使用多线程加速（10个并发线程）...", "info")
                
                high_price_orders = []
                price_filtered_count = 0
                failed_count = 0
                processed_count = 0
                
                # 定义获取单个订单详情的函数
                def fetch_ride_detail(ride_info):
                    try:
                        ride_id = ride_info['id']
                        detail = self.api_client.get(f'/fleet/rides/{ride_id}')
                        ride_detail = detail.get('ride', {})
                        vendor_amount = float(ride_detail.get('vendor_amount', 0) or 0)
                        passenger_name = ride_detail.get('passenger', {}).get('name', '未知')
                        
                        return {
                            'success': True,
                            'ride_id': ride_id,
                            'price': vendor_amount,
                            'pickup_time': ride_info['pickup_time'],
                            'passenger': passenger_name
                        }
                    except Exception as e:
                        return {
                            'success': False,
                            'ride_id': ride_info['id'],
                            'error': str(e)
                        }
                
                # 使用线程池并发请求
                with ThreadPoolExecutor(max_workers=10) as executor:
                    # 提交所有任务
                    future_to_ride = {executor.submit(fetch_ride_detail, ride): ride for ride in time_matched_rides}
                    
                    # 处理完成的任务
                    for future in as_completed(future_to_ride):
                        result = future.result()
                        processed_count += 1
                        
                        if result['success']:
                            # 显示前5个订单的详细信息
                            if processed_count <= 5:
                                self.log(f"  订单#{result['ride_id']}: 价格=${result['price']:.2f}, 时间={result['pickup_time']}", "info")
                            
                            # 检查价格
                            if result['price'] >= min_price:
                                high_price_orders.append({
                                    'id': result['ride_id'],
                                    'price': result['price'],
                                    'pickup_time': result['pickup_time'],
                                    'passenger': result['passenger']
                                })
                            else:
                                price_filtered_count += 1
                        else:
                            failed_count += 1
                            if failed_count <= 3:
                                self.log(f"  ✗ 订单#{result['ride_id']}获取失败: {result['error']}", "warning")
                        
                        # 进度显示
                        if processed_count % 50 == 0:
                            self.log(f"  进度: {processed_count}/{len(time_matched_rides)}", "info")
                
                if failed_count > 0:
                    self.log(f"  ⚠️ {failed_count} 个订单获取失败", "warning")
                if price_filtered_count > 0:
                    self.log(f"  💰 {price_filtered_count} 个订单价格低于阈值", "info")
                
                self.log(f"\n✓ 找到 {len(high_price_orders)} 个符合条件的高价订单", "success")
                
                if len(high_price_orders) == 0:
                    self.log("\n没有符合条件的订单", "warning")
                    self.set_status("就绪")
                    return
                
                # 显示前10个订单预览
                self.log(f"\n订单预览（前10个）:", "info")
                for i, order in enumerate(high_price_orders[:10], 1):
                    self.log(f"  {i}. 订单 {order['id']} - ${order['price']:.2f} - {order['pickup_time']} - {order['passenger']}")
                
                if len(high_price_orders) > 10:
                    self.log(f"  ...还有 {len(high_price_orders) - 10} 个订单")
                
                # 分配订单
                self.log(f"\n开始将订单分配到司机 {target_driver_id}...", "info")
                success_count = 0
                fail_count = 0
                
                for order in high_price_orders:
                    try:
                        # 使用dispatcher的assign_driver方法
                        result = self.dispatcher.assign_driver(order['id'], int(target_driver_id))
                        
                        if result.get('success'):
                            self.log(f"  ✓ 订单 {order['id']} (${order['price']:.2f})", "success")
                            success_count += 1
                        else:
                            self.log(f"  ✗ 订单 {order['id']} 分配失败: {result.get('error', '未知错误')}", "error")
                            fail_count += 1
                    except Exception as e:
                        self.log(f"  ✗ 订单 {order['id']} 分配失败: {e}", "error")
                        fail_count += 1
                
                self.log(f"\n{'='*60}")
                self.log(f"✓ 完成！成功: {success_count}, 失败: {fail_count}, 总计: {len(high_price_orders)}", "success")
                self.set_status("就绪")
                
            except Exception as e:
                self.log(f"\n✗ 筛选失败: {str(e)}", "error")
                self.set_status("就绪")
                logger.error(f"高价订单筛选失败: {e}", exc_info=True)
        
        threading.Thread(target=task, daemon=True).start()
    
    def show_auto_withdraw_dialog(self):
        """显示实时退工监控对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⏰ 实时退工监控")
        dialog.geometry("520x380")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (520 // 2)
        y = (dialog.winfo_screenheight() // 2) - (380 // 2)
        dialog.geometry(f"520x380+{x}+{y}")
        
        # 说明
        ttk.Label(dialog, text="监控指定司机的订单，在pick up时间前自动退工\n提前10分钟开始红色倒计时提醒", 
                 wraplength=450).pack(pady=15)
        
        # 输入区域
        input_frame = ttk.Frame(dialog)
        input_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # 司机ID列表
        ttk.Label(input_frame, text="订单池司机ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(input_frame, text="(每行一个ID，或用逗号分隔)", font=("Arial", 8)).grid(row=1, column=0, sticky=tk.W)
        
        driver_text = tk.Text(input_frame, width=40, height=6)
        driver_text.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        
        # 填充上次的司机ID
        if self.last_driver_ids:
            driver_text.insert("1.0", self.last_driver_ids)
        
        # 退工时间
        ttk.Label(input_frame, text="退工时间(分钟):").grid(row=2, column=0, sticky=tk.W, pady=5)
        minutes_var = tk.StringVar(value=self.last_withdraw_minutes)
        minutes_entry = ttk.Entry(input_frame, textvariable=minutes_var, width=40)
        minutes_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(input_frame, text="(在pick up时间前多少分钟退工，建议90分钟)", font=("Arial", 8)).grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        input_frame.columnconfigure(1, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def start_monitor():
            driver_ids_text = driver_text.get("1.0", tk.END).strip()
            minutes_str = minutes_var.get().strip()
            
            if not driver_ids_text or not minutes_str:
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            # 解析司机ID列表 - 支持逗号、分号、空格、换行等分隔符
            import re
            # 先按换行分割，再按逗号、分号、空格分割
            driver_ids = []
            for line in driver_ids_text.split('\n'):
                # 使用正则表达式分割：逗号、分号、空格、制表符
                ids = re.split('[,，;；\\s]+', line.strip())
                driver_ids.extend([id.strip() for id in ids if id.strip()])
            
            if len(driver_ids) == 0:
                messagebox.showerror("错误", "请至少输入一个司机ID")
                return
            
            # 去重
            driver_ids = list(set(driver_ids))
            
            try:
                minutes = int(minutes_str)
                if minutes <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "退工时间必须是正整数")
                return
            
            # 保存输入以便下次使用
            self.last_driver_ids = driver_ids_text
            self.last_withdraw_minutes = minutes_str
            self._save_settings()  # 保存到文件
            
            dialog.destroy()
            self.start_auto_withdraw(driver_ids, minutes)
        
        # 按钮布局优化
        if self.auto_withdraw_running:
            ttk.Button(btn_frame, text="⏸ 停止监控", command=lambda: self.stop_auto_withdraw(), width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="关闭", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(btn_frame, text="▶ 开始监控", command=start_monitor, width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
    
    def start_auto_withdraw(self, driver_ids, minutes_before):
        """启动实时退工监控"""
        if self.auto_withdraw_running:
            messagebox.showwarning("警告", "监控已在运行中")
            return
        
        # 创建监控日志窗口
        monitor_window = tk.Toplevel(self.root)
        monitor_window.title("⏰ 实时退工监控 - 运行中")
        monitor_window.geometry("700x500")
        
        # 居中显示
        monitor_window.update_idletasks()
        x = (monitor_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (monitor_window.winfo_screenheight() // 2) - (500 // 2)
        monitor_window.geometry(f"700x500+{x}+{y}")
        
        # 状态标签
        status_label = ttk.Label(monitor_window, text="监控运行中...", font=("Arial", 10, "bold"))
        status_label.pack(pady=10)
        
        # 日志区域
        log_frame = ttk.Frame(monitor_window)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        monitor_log = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD, font=("Consolas", 9))
        monitor_log.pack(fill=tk.BOTH, expand=True)
        
        # 配置日志颜色
        monitor_log.tag_config("info", foreground="blue")
        monitor_log.tag_config("success", foreground="green")
        monitor_log.tag_config("warning", foreground="orange")
        monitor_log.tag_config("error", foreground="red")
        monitor_log.tag_config("countdown", foreground="purple", font=("Consolas", 9, "bold"))
        
        def log_to_monitor(msg, level="info"):
            """输出到监控窗口"""
            timestamp = datetime.now().strftime('%H:%M:%S')
            monitor_log.insert(tk.END, f"[{timestamp}] {msg}\n", level)
            monitor_log.see(tk.END)
            monitor_log.update()
        
        # 按钮区域
        btn_frame = ttk.Frame(monitor_window)
        btn_frame.pack(pady=10)
        
        def close_monitor():
            self.stop_auto_withdraw()
            monitor_window.destroy()
        
        close_btn = ttk.Button(btn_frame, text="🛑 停止并关闭", command=close_monitor, width=20)
        close_btn.pack()
        
        # 设置窗口关闭事件
        monitor_window.protocol("WM_DELETE_WINDOW", close_monitor)
        
        self.auto_withdraw_running = True
        
        log_to_monitor("="*60, "info")
        log_to_monitor("⏰ 启动实时退工监控", "success")
        log_to_monitor(f"监控司机: {', '.join(driver_ids)}", "info")
        log_to_monitor(f"退工时间: pick up前 {minutes_before} 分钟", "info")
        log_to_monitor(f"倒计时: 提前10分钟开始 (红色显示)", "info")
        log_to_monitor(f"详细信息: 仅显示2小时内的订单", "info")
        log_to_monitor("="*60, "info")
        log_to_monitor("", "info")
        
        def monitor_task():
            from real_api_scraper import RealAPIScraper
            if not self.real_scraper:
                self.real_scraper = RealAPIScraper(self.api_client)
            
            check_interval = 30  # 每30秒检查一次
            countdown_orders = {}  # 存储需要倒计时的订单 {ride_id: {'withdraw_time': datetime, 'info': {}}}
            
            while self.auto_withdraw_running:
                try:
                    current_time = datetime.now()
                    status_label.config(text=f"监控运行中... (每{check_interval}秒检查) - {current_time.strftime('%H:%M:%S')}")
                    
                    # 获取今天的订单
                    today = current_time.strftime('%Y-%m-%d')
                    
                    # 用于统计的字典
                    within_2h_orders = {}  # {driver_id: [(ride_id, pickup_time, withdraw_time_diff)]}
                    
                    for driver_id in driver_ids:
                        try:
                            # 获取assigned/accepted订单
                            log_to_monitor(f"🔍 检查司机 {driver_id}", "info")
                            rides = self.real_scraper.get_all_rides(
                                date=today, 
                                per_page=500,
                                statuses='assigned,accepted'
                            )
                            
                            # 筛选该司机的订单
                            driver_rides = [r for r in rides if str(r.get('driver_id')) == str(driver_id)]
                            
                            log_to_monitor(f"   共 {len(driver_rides)} 个订单", "info")
                            
                            if len(driver_rides) == 0:
                                continue
                            
                            within_2h_orders[driver_id] = []
                            
                            for ride in driver_rides:
                                try:
                                    ride_id = ride.get('id')
                                    pickup_at_str = ride.get('pickup_at', '')
                                    passenger = ride.get('passenger_name', '未知')
                                    
                                    if not pickup_at_str:
                                        continue
                                    
                                    # 解析pick up时间
                                    if 'T' in pickup_at_str:
                                        pickup_time = datetime.fromisoformat(pickup_at_str.replace('Z', '+00:00'))
                                        # 转换为本地时间
                                        ny_tz = pytz.timezone('America/New_York')
                                        pickup_time = pickup_time.astimezone(ny_tz)
                                        pickup_time = pickup_time.replace(tzinfo=None)  # 移除时区信息便于比较
                                    else:
                                        pickup_time = datetime.strptime(pickup_at_str, '%Y-%m-%d %H:%M:%S')
                                    
                                    # 计算时间差（分钟）
                                    time_diff_minutes = (pickup_time - current_time).total_seconds() / 60
                                    
                                    # 计算退工时间点
                                    withdraw_time = pickup_time - timedelta(minutes=minutes_before)
                                    withdraw_time_diff = (withdraw_time - current_time).total_seconds() / 60
                                    
                                    # 如果订单太远未来（超出监控范围）
                                    if time_diff_minutes > minutes_before:
                                        # 超出监控范围，跳过
                                        continue
                                    
                                    # 记录2小时内的订单
                                    if time_diff_minutes <= 120:
                                        pickup_time_str = pickup_time.strftime('%H:%M')
                                        within_2h_orders[driver_id].append({
                                            'ride_id': ride_id,
                                            'pickup_time': pickup_time_str,
                                            'time_to_pickup': int(time_diff_minutes),
                                            'time_to_withdraw': int(withdraw_time_diff)
                                        })
                                    
                                    # 如果已经过了退工时间或pickup时间（需要立即退工）
                                    if withdraw_time_diff <= 0:
                                        # 检查是否已经处理过（避免重复退工）
                                        if ride_id not in countdown_orders or not countdown_orders[ride_id].get('processed'):
                                            passenger = ride.get('passenger_name', '未知')
                                            pickup_time_str = pickup_time.strftime('%H:%M')
                                            
                                            log_to_monitor(f"", "info")
                                            log_to_monitor(f"⚡ 执行自动退工 (已到退工时间)", "warning")
                                            log_to_monitor(f"   订单ID: {ride_id}", "info")
                                            log_to_monitor(f"   乘客: {passenger}", "info")
                                            log_to_monitor(f"   司机ID: {driver_id}", "info")
                                            log_to_monitor(f"   Pick Up: {pickup_time_str}", "info")
                                            
                                            # 执行退工
                                            try:
                                                self.dispatcher.cancel_ride(ride_id, reason="Driver Cancel")
                                                log_to_monitor(f"   ✓ 退工成功", "success")
                                                
                                                # 同时输出到主窗口
                                                self.log(f"✓ 自动退工成功: 订单 {ride_id} - {passenger} (司机 {driver_id})", "success")
                                                
                                            except Exception as e:
                                                error_msg = str(e)
                                                if "404" in error_msg:
                                                    log_to_monitor(f"   ✗ 退工失败: 订单不允许退工 (404)", "error")
                                                elif "403" in error_msg:
                                                    log_to_monitor(f"   ✗ 退工失败: 无权限 (403)", "error")
                                                else:
                                                    log_to_monitor(f"   ✗ 退工失败: {e}", "error")
                                                
                                                self.log(f"✗ 自动退工失败: 订单 {ride_id} - {e}", "error")
                                            
                                            log_to_monitor(f"", "info")
                                            
                                            # 标记为已处理
                                            countdown_orders[ride_id] = {
                                                'processed': True,
                                                'withdraw_time': withdraw_time,
                                                'pickup_time': pickup_time,
                                                'passenger': passenger,
                                                'driver_id': driver_id,
                                                'pickup_time_str': pickup_time_str
                                            }
                                        continue
                                    
                                    # 如果在倒计时范围内（退工前10分钟以内）
                                    if 0 < withdraw_time_diff <= 10:
                                        if ride_id not in countdown_orders:
                                            # 第一次进入倒计时
                                            pickup_time_str = pickup_time.strftime('%H:%M')
                                            
                                            countdown_orders[ride_id] = {
                                                'withdraw_time': withdraw_time,
                                                'pickup_time': pickup_time,
                                                'passenger': passenger,
                                                'driver_id': driver_id,
                                                'pickup_time_str': pickup_time_str,
                                                'processed': False
                                            }
                                            
                                            log_to_monitor(f"", "info")
                                            log_to_monitor(f"🔔 订单 {ride_id} 进入倒计时: {int(withdraw_time_diff)}分{int((withdraw_time_diff % 1) * 60)}秒", "error")
                                            log_to_monitor(f"", "info")
                                        else:
                                            # 更新倒计时（使用红色显示）
                                            if not countdown_orders[ride_id].get('processed'):
                                                # 每次检查都更新
                                                countdown_orders[ride_id]['withdraw_time'] = withdraw_time
                                                countdown_orders[ride_id]['pickup_time'] = pickup_time
                                
                                except Exception as e:
                                    log_to_monitor(f"   ✗ 处理订单 {ride.get('id', '未知')} 出错: {e}", "error")
                                    import traceback
                                    log_to_monitor(f"      {traceback.format_exc()}", "error")
                                    continue
                        
                        except Exception as e:
                            log_to_monitor(f"✗ 获取司机{driver_id}订单失败: {e}", "error")
                            import traceback
                            log_to_monitor(f"   {traceback.format_exc()}", "error")
                            continue
                    
                    # 显示2小时内的订单汇总
                    total_2h_orders = sum(len(orders) for orders in within_2h_orders.values())
                    if total_2h_orders > 0:
                        log_to_monitor(f"", "info")
                        log_to_monitor(f"="*60, "info")
                        log_to_monitor(f"📅 2小时内订单: {total_2h_orders} 个", "info")
                        for driver_id, orders in within_2h_orders.items():
                            if len(orders) > 0:
                                log_to_monitor(f"   司机{driver_id}: {len(orders)}个订单", "info")
                                # 按退工时间排序，显示所有订单的倒计时
                                sorted_orders = sorted(orders, key=lambda x: x['time_to_withdraw'])
                                for order in sorted_orders:
                                    # 显示倒计时（到退工时间）
                                    time_to_withdraw = order['time_to_withdraw']
                                    if time_to_withdraw > 0:
                                        # 转换为分钟和秒
                                        mins = int(time_to_withdraw)
                                        secs = int((time_to_withdraw - mins) * 60)
                                        # 如果在10分钟以内，用红色显示
                                        if time_to_withdraw <= 10:
                                            log_to_monitor(f"      ⏰ 订单{order['ride_id']} (Pickup: {order['pickup_time']}): 退工倒计时 {mins}分{secs}秒", "error")
                                        else:
                                            log_to_monitor(f"      订单{order['ride_id']} (Pickup: {order['pickup_time']}): 退工倒计时 {mins}分{secs}秒", "info")
                                    else:
                                        log_to_monitor(f"      订单{order['ride_id']} (Pickup: {order['pickup_time']}): 已到退工时间", "warning")
                        log_to_monitor(f"="*60, "info")
                    
                    # 检查完所有司机后，显示当前倒计时的订单
                    active_countdowns = {k: v for k, v in countdown_orders.items() if not v.get('processed')}
                    if active_countdowns:
                        log_to_monitor(f"", "info")
                        log_to_monitor(f"="*60, "info")
                        log_to_monitor(f"⏰ 倒计时订单(最后10分钟): {len(active_countdowns)} 个", "warning")
                        for ride_id, info in active_countdowns.items():
                            time_left = (info['withdraw_time'] - current_time).total_seconds() / 60
                            if time_left > 0:
                                log_to_monitor(f"   订单 {ride_id} (司机{info['driver_id']}, Pickup: {info.get('pickup_time_str', 'N/A')}): 退工还有 {int(time_left)}分{int((time_left % 1) * 60)}秒", "error")
                        log_to_monitor(f"="*60, "info")
                        log_to_monitor(f"", "info")
                    
                    # 等待下一次检查
                    import time
                    for _ in range(check_interval):
                        if not self.auto_withdraw_running:
                            break
                        time.sleep(1)
                
                except Exception as e:
                    log_to_monitor(f"✗ 监控出错: {e}", "error")
                    import time
                    time.sleep(check_interval)
            
            log_to_monitor("", "info")
            log_to_monitor("="*60, "info")
            log_to_monitor("⏰ 实时退工监控已停止", "warning")
            log_to_monitor("="*60, "info")
            status_label.config(text="监控已停止")
            close_btn.config(text="关闭", command=monitor_window.destroy)
            
            self.log(f"\n⏰ 实时退工监控已停止", "warning")
            self.set_status("就绪")
        
        self.auto_withdraw_thread = threading.Thread(target=monitor_task, daemon=True)
        self.auto_withdraw_thread.start()
    
    def stop_auto_withdraw(self):
        """停止实时退工监控"""
        if self.auto_withdraw_running:
            self.auto_withdraw_running = False
            self.log(f"\n正在停止监控...", "warning")
            messagebox.showinfo("提示", "监控将在下次检查周期后停止")
        else:
            messagebox.showinfo("提示", "监控未运行")


def main():
    root = tk.Tk()
    app = DispatchManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
