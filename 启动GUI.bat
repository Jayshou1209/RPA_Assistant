@echo off
chcp 65001 >nul
echo ========================================
echo 启动 RPA自动化系统 - GUI界面
echo ========================================
echo.

cd /d "%~dp0"

echo [检查Python环境...]
py --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [启动GUI程序...]
echo.

py gui.py

if errorlevel 1 (
    echo.
    echo 程序执行出错，请检查错误信息
    pause
)
