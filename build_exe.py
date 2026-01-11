# RPA助手打包脚本 (Python版本)
import os
import sys
import shutil
import subprocess

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def run_command(cmd, description):
    print(f"执行: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    print_header("RPA助手打包工具")
    
    # 1. 检查PyInstaller
    print("[1/5] 检查PyInstaller...")
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        if not run_command("pip install pyinstaller", "安装PyInstaller"):
            print("安装失败，请手动安装: pip install pyinstaller")
            return False
    
    # 2. 清理旧文件
    print("\n[2/5] 清理旧文件...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ 已删除 {folder} 文件夹")
    
    if os.path.exists("RPA调度助手.spec"):
        os.remove("RPA调度助手.spec")
        print("✓ 已删除旧的spec文件")
    
    # 3. 准备打包命令
    print("\n[3/5] 准备打包参数...")
    
    # 所有需要的隐藏导入
    hidden_imports = [
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 
        'tkinter.scrolledtext', 'api_client', 'scraper', 'dispatcher',
        'enhanced_scraper', 'real_api_scraper', 'gui_dispatcher', 'gui_scraper',
        'pandas', 'openpyxl', 'requests', 'pytz', 'concurrent.futures'
    ]
    
    hidden_import_args = ' '.join([f'--hidden-import={imp}' for imp in hidden_imports])
    
    # 添加当前目录到Python路径中的所有.py文件
    py_files = ['api_client.py', 'scraper.py', 'dispatcher.py', 'enhanced_scraper.py', 
                'real_api_scraper.py', 'gui_dispatcher.py', 'gui_scraper.py']
    add_data_args = ' '.join([f'--add-data="{f};."' for f in py_files if os.path.exists(f)])
    
    # 构建打包命令
    cmd = f'''pyinstaller --clean --onefile --windowed --name="RPA调度助手" '''
    cmd += f'''--add-data="config.py;." --add-data="token.txt;." '''
    cmd += f'''{add_data_args} '''
    cmd += f'''{hidden_import_args} launcher.py'''
    
    # 4. 执行打包
    print("\n[4/5] 开始打包...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    if not run_command(cmd, "打包程序"):
        print("\n打包失败！请检查错误信息")
        return False
    
    # 5. 检查结果
    print("\n[5/5] 检查打包结果...")
    exe_path = os.path.join("dist", "RPA调度助手.exe")
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print_header("打包成功！")
        print(f"生成的文件: {exe_path}")
        print(f"文件大小: {size_mb:.2f} MB")
        print("\n使用说明:")
        print("1. 将 config.py 和 token.txt 复制到exe所在目录")
        print("2. 创建 data 文件夹用于存储数据")
        print("3. 双击运行 RPA调度助手.exe")
        print("\n" + "=" * 60)
        
        # 打开dist文件夹
        if sys.platform == 'win32':
            os.startfile('dist')
        
        return True
    else:
        print("✗ 未找到生成的exe文件")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
