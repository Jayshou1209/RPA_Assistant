"""
RPA自动化助手 - 主启动器
统一管理所有功能模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
from pathlib import Path


class RPALauncher:
    """RPA系统主启动器"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RPA自动化助手 v2.0")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # 设置窗口图标颜色
        self.root.configure(bg="#f0f0f0")
        
        # 创建主界面
        self.create_widgets()
        
        # 居中显示
        self.center_window()
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题区域
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🚀 RPA 调度系统自动化助手",
            font=("微软雅黑", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            title_frame,
            text="一站式数据管理与调度解决方案",
            font=("微软雅黑", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # 主内容区域
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 1. 功能模块区域
        self.create_modules_section(main_frame)
        
        # 2. 系统管理区域
        self.create_system_section(main_frame)
        
        # 底部状态栏
        self.create_status_bar()
    
    def create_modules_section(self, parent):
        """创建功能模块区域"""
        modules_frame = tk.LabelFrame(
            parent,
            text="📊 功能模块",
            font=("微软雅黑", 11, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
            padx=15,
            pady=15
        )
        modules_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建两列布局
        left_frame = tk.Frame(modules_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_frame = tk.Frame(modules_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 数据爬取模块
        self.create_module_card(
            left_frame,
            "📊 数据爬取工具",
            "爬取司机、排班、订单数据\n生成账单和报表",
            "#3498db",
            self.launch_scraper
        )
        
        # 调度管理模块
        self.create_module_card(
            right_frame,
            "🎯 调度管理工具",
            "派工、转派、退工\n司机订单管理",
            "#e74c3c",
            self.launch_dispatcher
        )
    
    def create_module_card(self, parent, title, description, color, command):
        """创建模块卡片"""
        card = tk.Frame(parent, bg="white", relief=tk.RAISED, borderwidth=1)
        card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 颜色条
        color_bar = tk.Frame(card, bg=color, height=5)
        color_bar.pack(fill=tk.X)
        
        content_frame = tk.Frame(card, bg="white", padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(
            content_frame,
            text=title,
            font=("微软雅黑", 12, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 描述
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=("微软雅黑", 9),
            bg="white",
            fg="#7f8c8d",
            justify=tk.LEFT
        )
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 启动按钮
        btn = tk.Button(
            content_frame,
            text="启动模块",
            font=("微软雅黑", 10, "bold"),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=command,
            padx=20,
            pady=8
        )
        btn.pack(anchor=tk.W)
        
        # 鼠标悬停效果
        def on_enter(e):
            btn.config(relief=tk.RAISED)
        
        def on_leave(e):
            btn.config(relief=tk.FLAT)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def create_system_section(self, parent):
        """创建系统管理区域"""
        system_frame = tk.LabelFrame(
            parent,
            text="⚙️ 系统管理",
            font=("微软雅黑", 11, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
            padx=15,
            pady=15
        )
        system_frame.pack(fill=tk.X)
        
        # 按钮容器
        buttons_frame = tk.Frame(system_frame, bg="#f0f0f0")
        buttons_frame.pack(fill=tk.X)
        
        # 创建系统管理按钮
        buttons = [
            ("✓ 测试连接", self.test_connection, "#27ae60"),
            ("🔧 安装依赖", self.install_dependencies, "#95a5a6"),
            ("🔑 更新Token", self.update_token, "#f39c12"),
            ("📁 打开数据目录", self.open_data_folder, "#16a085"),
            ("ℹ️ 关于", self.show_about, "#34495e")
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(
                buttons_frame,
                text=text,
                font=("微软雅黑", 9),
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief=tk.FLAT,
                cursor="hand2",
                command=command,
                width=15,
                pady=8
            )
            btn.grid(row=i//5, column=i%5, padx=5, pady=5, sticky=tk.EW)
            
            # 鼠标悬停效果
            def make_hover(button):
                def on_enter(e):
                    button.config(relief=tk.RAISED)
                def on_leave(e):
                    button.config(relief=tk.FLAT)
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)
            
            make_hover(btn)
        
        # 配置列权重
        for i in range(5):
            buttons_frame.columnconfigure(i, weight=1)
    
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("微软雅黑", 9),
            bg="#34495e",
            fg="white",
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        version_label = tk.Label(
            status_frame,
            text="v2.0",
            font=("微软雅黑", 9),
            bg="#34495e",
            fg="#95a5a6"
        )
        version_label.pack(side=tk.RIGHT, padx=10)
    
    def set_status(self, message):
        """设置状态信息"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    # ==================== 功能方法 ====================
    
    def launch_scraper(self):
        """启动数据爬取工具"""
        try:
            self.set_status("正在启动数据爬取工具...")
            
            # 动态导入GUI模块
            try:
                from gui_scraper import DataScraperGUI
            except ImportError as import_error:
                raise ImportError(f"无法导入gui_scraper模块: {import_error}")
            
            # 创建新窗口
            scraper_root = tk.Toplevel(self.root)
            app = DataScraperGUI(scraper_root)
            
            self.set_status("数据爬取工具已启动")
            messagebox.showinfo("成功", "数据爬取工具已启动！")
        except Exception as e:
            self.set_status("启动失败")
            messagebox.showerror("错误", f"启动数据爬取工具失败:\n{e}")
    
    def launch_dispatcher(self):
        """启动调度管理工具"""
        try:
            self.set_status("正在启动调度管理工具...")
            
            # 动态导入GUI模块
            try:
                from gui_dispatcher import DispatchManagerGUI
            except ImportError as import_error:
                raise ImportError(f"无法导入gui_dispatcher模块: {import_error}")
            
            # 创建新窗口
            dispatcher_root = tk.Toplevel(self.root)
            app = DispatchManagerGUI(dispatcher_root)
            
            self.set_status("调度管理工具已启动")
            messagebox.showinfo("成功", "调度管理工具已启动！")
        except Exception as e:
            self.set_status("启动失败")
            messagebox.showerror("错误", f"启动调度管理工具失败:\n{e}")
    
    def install_dependencies(self):
        """安装依赖"""
        result = messagebox.askyesno(
            "安装依赖",
            "即将安装所有必需的Python依赖包\n\n这可能需要几分钟时间\n\n确定要继续吗？"
        )
        
        if result:
            try:
                self.set_status("正在安装依赖...")
                # 创建新窗口显示安装过程
                install_window = tk.Toplevel(self.root)
                install_window.title("安装依赖")
                install_window.geometry("600x400")
                install_window.transient(self.root)
                
                text_widget = tk.Text(install_window, wrap=tk.WORD, font=("Consolas", 9))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                text_widget.insert(tk.END, "开始安装依赖...\n\n")
                text_widget.update()
                
                # 执行安装
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    text_widget.insert(tk.END, line)
                    text_widget.see(tk.END)
                    text_widget.update()
                
                process.wait()
                
                if process.returncode == 0:
                    text_widget.insert(tk.END, "\n✓ 依赖安装成功！\n")
                    self.set_status("依赖安装成功")
                    messagebox.showinfo("成功", "所有依赖已安装完成！")
                else:
                    text_widget.insert(tk.END, "\n✗ 依赖安装失败\n")
                    self.set_status("依赖安装失败")
                
            except Exception as e:
                self.set_status("安装失败")
                messagebox.showerror("错误", f"安装依赖失败:\n{e}")
    
    def update_token(self):
        """更新Token"""
        try:
            self.set_status("正在启动Token更新工具...")
            # 获取当前脚本所在目录
            if getattr(sys, 'frozen', False):
                # 如果是打包的exe
                current_dir = os.path.dirname(sys.executable)
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
            
            token_gui_path = os.path.join(current_dir, "update_token_gui.py")
            
            # 检查文件是否存在
            if not os.path.exists(token_gui_path):
                # 打包后的程序中，直接在当前窗口更新
                self.update_token_inline()
                return
            
            # 使用pythonw.exe隐藏控制台窗口
            python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
            if not os.path.exists(python_exe):
                python_exe = sys.executable
            
            subprocess.Popen([python_exe, token_gui_path],
                           cwd=current_dir,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.set_status("Token更新工具已启动")
            
            # 提示用户更新后需要测试
            messagebox.showinfo(
                "提示",
                "Token更新工具已启动。\n\n"
                "更新完成后，请点击'测试连接'按钮验证新Token是否有效。"
            )
        except Exception as e:
            self.set_status("启动失败")
            messagebox.showerror("错误", f"启动Token更新工具失败:\n{e}")
    
    def update_token_inline(self):
        """内嵌的Token更新对话框（用于打包后的程序）"""
        # 创建更新对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("更新Token")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350)
        y = (dialog.winfo_screenheight() // 2) - (250)
        dialog.geometry(f"700x500+{x}+{y}")
        
        # 说明
        instruction_frame = tk.LabelFrame(dialog, text="📖 获取Token步骤", padx=10, pady=10)
        instruction_frame.pack(fill=tk.X, padx=10, pady=10)
        
        instructions = """1. 打开浏览器，访问: https://admin.myle.tech
2. 登录你的账户
3. 按 F12 打开浏览器开发者工具
4. 切换到 Network (网络) 标签
5. 在页面中执行任何操作（如点击菜单）
6. 在 Network 列表中找到任意请求
7. 查看 Request Headers (请求头)
8. 找到 Authorization 字段，复制完整的值（包括 "Bearer " 前缀）
9. 粘贴到下方文本框中"""
        
        tk.Label(instruction_frame, text=instructions, justify=tk.LEFT, anchor=tk.W, font=("Arial", 9)).pack()
        
        # Token输入
        token_frame = tk.LabelFrame(dialog, text="🔑 输入新Token", padx=10, pady=10)
        token_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(token_frame, text="Token (必须以 'Bearer ' 开头):").pack(anchor=tk.W)
        
        from tkinter import scrolledtext
        token_text = scrolledtext.ScrolledText(token_frame, height=6, wrap=tk.WORD)
        token_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        def save_token():
            new_token = token_text.get("1.0", tk.END).strip()
            
            if not new_token:
                messagebox.showerror("错误", "Token不能为空！", parent=dialog)
                return
            
            if not new_token.startswith("Bearer "):
                messagebox.showerror("错误", "Token必须以 'Bearer ' 开头！\n\n请确保复制了完整的Authorization值。", parent=dialog)
                return
            
            if len(new_token) < 100:
                if not messagebox.askyesno("警告", f"Token看起来太短了（{len(new_token)}字符）。\n\n确定要继续吗？", parent=dialog):
                    return
            
            try:
                # 更新token.txt
                if getattr(sys, 'frozen', False):
                    token_file = os.path.join(os.path.dirname(sys.executable), "token.txt")
                else:
                    token_file = os.path.join(os.path.dirname(__file__), "token.txt")
                
                with open(token_file, 'w', encoding='utf-8') as f:
                    f.write(new_token)
                
                messagebox.showinfo(
                    "成功",
                    f"Token已更新！\n\n"
                    f"✓ 已保存到: token.txt\n"
                    f"✓ Token长度: {len(new_token)} 字符\n\n"
                    f"请点击'测试连接'按钮验证新Token。",
                    parent=dialog
                )
                dialog.destroy()
                self.set_status("Token已更新，请测试连接")
            except Exception as e:
                messagebox.showerror("错误", f"保存Token失败:\n\n{e}", parent=dialog)
        
        # 按钮
        btn_frame = tk.Frame(token_frame)
        btn_frame.pack()
        
        tk.Button(btn_frame, text="✓ 保存Token", command=save_token,
                 bg="#27ae60", fg="white", padx=20, pady=8, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✗ 取消", command=dialog.destroy,
                 padx=20, pady=8, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def open_data_folder(self):
        """打开数据目录"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            os.startfile(data_dir)
            self.set_status("数据目录已打开")
        except Exception as e:
            messagebox.showerror("错误", f"打开数据目录失败:\n{e}")
    
    def test_connection(self):
        """测试API连接"""
        try:
            # 重新加载config以获取最新的token
            import importlib
            import config
            importlib.reload(config)
            
            from api_client import APIClient
            
            self.set_status("正在测试连接...")
            self.root.update()
            
            # 检查token是否为空或默认值
            if not config.BEARER_TOKEN or config.BEARER_TOKEN == "Bearer" or len(config.BEARER_TOKEN) < 50:
                self.set_status("Token无效")
                messagebox.showerror(
                    "Token无效",
                    "✗ Token为空或无效\n\n"
                    "请先点击'更新Token'按钮配置有效的Token。"
                )
                return
            
            api = APIClient(config.BEARER_TOKEN)
            success, message = api.verify_connection()
            
            if success:
                self.set_status("连接成功！")
                messagebox.showinfo(
                    "连接成功",
                    f"✓ API连接正常\n\n"
                    f"服务器: {config.API_BASE_URL}\n"
                    f"{message}"
                )
            else:
                self.set_status("连接失败")
                messagebox.showerror(
                    "连接失败",
                    f"✗ 连接验证失败\n\n"
                    f"{message}\n\n"
                    "请点击'更新Token'按钮更新Token。"
                )
        except Exception as e:
            self.set_status("连接错误")
            messagebox.showerror("错误", f"连接测试失败：\n{str(e)}")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
RPA 调度系统自动化助手 v2.0

一站式数据管理与调度解决方案

主要功能：
• 数据爬取 - 司机、排班、订单数据采集
• 账单生成 - 自动统计和生成账单报表
• 调度管理 - 派工、转派、退工操作
• Token管理 - 便捷的Token更新工具

技术栈：
• Python 3.12
• Tkinter GUI
• RESTful API

© 2025 RPA Team. All rights reserved.
        """
        
        messagebox.showinfo("关于", about_text)


def main():
    root = tk.Tk()
    app = RPALauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
