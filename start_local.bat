@echo off
chcp 65001 >nul
echo ========================================
echo      启动本地开发环境
echo ========================================

REM 设置环境变量启用本地配置文件
set USE_LOCAL_CONFIG=true

echo 环境变量设置:
echo USE_LOCAL_CONFIG=%USE_LOCAL_CONFIG%
echo.

echo 将使用 cfg.ini.local 配置文件
echo.

REM 启动Python应用
echo 正在启动应用...
python run_server.py

pause
