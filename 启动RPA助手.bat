@echo off
chcp 65001 >nul

REM 使用 pythonw.exe 隐藏控制台窗口
start "" pythonw launcher.py

REM 如果 pythonw 不存在，使用普通 python
if errorlevel 1 (
    start "" python launcher.py
)
