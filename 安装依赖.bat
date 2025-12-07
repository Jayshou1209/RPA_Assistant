@echo off
chcp 65001 >nul
echo ========================================
echo 安装RPA自动化脚本依赖
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 检查Python环境...
py --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo [2/2] 安装依赖包...
py -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 安装失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 编辑 config.py 更新每日Token
echo 2. 运行 启动脚本.bat 或 python main.py
echo.
pause
