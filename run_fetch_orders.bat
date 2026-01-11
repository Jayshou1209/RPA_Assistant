@echo off
chcp 65001 >nul
start "" pythonw fetch_orders_gui.py
if errorlevel 1 start "" python fetch_orders_gui.py
