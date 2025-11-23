# -*- coding:utf-8 -*-
"""
Flask应用主入口文件
"""
from quier_flask import route_ctrl
from quier_flask import app, cfg

# 初始化日志
route_ctrl.init_service_log()

if __name__ == '__main__':
    HOST = cfg.server_host
    PORT = cfg.server_port
    print(f'启动Flask应用: http://{HOST}:{PORT}')
    app.run(HOST, PORT, debug=False, threaded=True)
