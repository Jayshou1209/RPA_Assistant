@echo off
chcp 65001 >nul
echo 正在爬取订单数据...
echo.
pythonw fetch_orders_to_file.py
if errorlevel 1 python fetch_orders_to_file.py
