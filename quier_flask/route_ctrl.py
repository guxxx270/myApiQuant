# -*- coding:utf-8 -*-
import functools
import logging
import os
import traceback
from logging import handlers
from flask import jsonify, request

from quier_flask import app, cfg

route_logger = logging.getLogger("service")
app.secret_key = '123456789'


def init_service_log():
    """初始化日志配置"""
    route_logger.setLevel(cfg.loglevel)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(os.path.dirname(cur_path), "logs")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_file = os.path.join(log_path, "service.log")
    if not os.path.exists(log_file):
        os.system(r"touch {}".format(log_file))

    fh = handlers.TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=40)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    route_logger.addHandler(fh)


def get_traceback(e):
    """获取异常详细信息"""
    traceback_details = {
        "type": type(e).__name__,
        "message": str(e),
        "traceback": traceback.format_exc()
    }
    return traceback_details


def ctrl_handler():
    """路由装饰器 - 处理请求和异常"""
    def pre_ctrl_handler(f):
        @functools.wraps(f)
        def inner_ctrl_handler(*args, **kws):
            route_logger.debug(request)
            req = request.get_json(silent=True)
            try:
                response = f(req)
            except Exception as e:
                route_logger.error('错误请求路径:%s | 请求参数:%s', request.path, req)
                route_logger.error('错误响应:%s', get_traceback(e))
                response = {'code': 4003, 'msg': format(get_traceback(e))}
            return jsonify(response)

        return inner_ctrl_handler

    return pre_ctrl_handler


# ========== 路由定义 ==========

# 存活性检查
@app.route('/hello/testSuccess', methods=["GET"])
@ctrl_handler()
def test(req):
    """健康检查接口"""
    return {"code": 0, "data": "ok", "msg": "success"}


@app.route('/api/example', methods=["POST"])
@ctrl_handler()
def example_api(req):
    """示例API接口"""
    return {
        "code": 0,
        "msg": "成功",
        "data": {
            "message": "这是一个示例API",
            "request": req
        }
    }
