@echo off
chcp 65001 >nul
title Token连接测试
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Token 连接测试工具                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

python test_token.py

echo.
pause
