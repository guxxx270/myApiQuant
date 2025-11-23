@echo off
chcp 65001 >nul
echo ========================================
echo      启动生产服务器
echo ========================================

REM 启动Python应用（使用默认cfg.ini配置）
echo 正在启动应用...
python run_server.py

pause
