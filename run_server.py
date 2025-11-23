# -*- coding:utf-8 -*-
"""
Flask应用主入口文件
"""
from quier_flask import route_ctrl
from quier_flask import app, cfg
from apps.service.startup_init import init_app_startup

# 初始化日志
route_ctrl.init_service_log()

# 应用启动初始化（推送最近交易、启动定时监控）
init_app_startup()

if __name__ == '__main__':
    HOST = cfg.server_host
    PORT = cfg.server_port
    print(f'启动Flask应用: http://{HOST}:{PORT}')
    app.run(HOST, PORT, debug=False, threaded=True)
