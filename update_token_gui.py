"""
简单的Token更新工具 - GUI版本
用于快速更新过期的Token
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import re
from datetime import datetime

class TokenUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("Token 更新工具")
        self.root.geometry("800x500")
        
        # 说明文本
        instruction_frame = tk.LabelFrame(root, text="📖 获取Token步骤", padx=10, pady=10)
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
        
        tk.Label(instruction_frame, text=instructions, justify=tk.LEFT, anchor=tk.W).pack()
        
        # Token输入区域
        token_frame = tk.LabelFrame(root, text="🔑 输入新Token", padx=10, pady=10)
        token_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(token_frame, text="Token (必须以 'Bearer ' 开头):").pack(anchor=tk.W)
        
        self.token_text = scrolledtext.ScrolledText(token_frame, height=8, wrap=tk.WORD)
        self.token_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # 按钮
        btn_frame = tk.Frame(token_frame)
        btn_frame.pack()
        
        tk.Button(btn_frame, text="✓ 更新Token", command=self.update_token, 
                 bg="green", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✗ 取消", command=self.root.quit,
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        status_label = tk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def update_token(self):
        """更新Token"""
        new_token = self.token_text.get("1.0", tk.END).strip()
        
        # 验证Token格式
        if not new_token:
            messagebox.showerror("错误", "Token不能为空！")
            return
        
        if not new_token.startswith("Bearer "):
            messagebox.showerror("错误", "Token必须以 'Bearer ' 开头！\n\n请确保复制了完整的Authorization值。")
            return
        
        # 检查Token长度（JWT通常较长）
        if len(new_token) < 100:
            if not messagebox.askyesno("警告", f"Token看起来太短了（{len(new_token)}字符）。\n\n确定要继续吗？"):
                return
        
        try:
            self.status_var.set("正在更新...")
            
            # 更新 token.txt（不带BOM）
            token_file = os.path.join(os.path.dirname(__file__), "token.txt")
            with open(token_file, 'w', encoding='utf-8') as f:
                f.write(new_token)
            
            # 备份 config.py
            config_file = os.path.join(os.path.dirname(__file__), "config.py")
            if os.path.exists(config_file):
                backup_file = f"config.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 更新 config.py（可选，因为config.py会从token.txt读取）
                # 但为了保持一致性，也更新config.py
                pattern = r'BEARER_TOKEN = _load_token\(\)'
                if pattern in content:
                    # config.py使用_load_token()，不需要手动更新
                    pass
                else:
                    # 旧版本的config.py，需要手动更新
                    pattern = r'BEARER_TOKEN = "Bearer [^"]*"'
                    replacement = f'BEARER_TOKEN = "{new_token}"'
                    content = re.sub(pattern, replacement, content)
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            self.status_var.set("更新成功！")
            messagebox.showinfo(
                "成功", 
                f"Token已更新！\n\n"
                f"✓ 已保存到: token.txt\n"
                f"✓ Token长度: {len(new_token)} 字符\n\n"
                f"请重新启动应用程序以使用新Token。"
            )
            self.root.quit()
            
        except Exception as e:
            self.status_var.set(f"更新失败: {e}")
            messagebox.showerror("错误", f"更新Token失败:\n\n{e}")

def main():
    root = tk.Tk()
    app = TokenUpdater(root)
    root.mainloop()

if __name__ == "__main__":
    main()
