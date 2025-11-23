# -*- coding:utf-8 -*-
import functools
import logging
import os
import traceback
from logging import handlers
from flask import jsonify, request

from quier_flask import app, cfg
from apps.service.monitor_service import monitor_service
from apps.service.monitor_scheduler import scheduler
from apps.utiles.wechat_util import wechat_api_info, wechat_api_warning

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


# ========== 交易监控接口 ==========

@app.route('/api/monitor/fetch_trades', methods=["POST"])
@ctrl_handler()
def fetch_trades_api(req):
    """
    获取交易数据接口

    请求参数:
        model_code: 模型代码 (可选, 默认: pandaai)
        page: 页码 (可选, 默认: 1)
        limit: 每页数量 (可选, 默认: 50)
    """
    model_code = req.get("model_code") if req else None
    page = req.get("page") if req else None
    limit = req.get("limit") if req else None

    result = monitor_service.fetch_trades(model_code, page, limit)

    if result["success"]:
        return {
            "code": 0,
            "msg": "成功",
            "data": result
        }
    else:
        return {
            "code": -1,
            "msg": f"获取数据失败: {result.get('error')}",
            "data": result
        }


@app.route('/api/monitor/check_new_trades', methods=["POST"])
@ctrl_handler()
def check_new_trades_api(req):
    """
    检查新交易接口

    请求参数:
        model_code: 模型代码 (可选, 默认: pandaai)
        page: 页码 (可选, 默认: 1)
        limit: 每页数量 (可选, 默认: 50)
    """
    model_code = req.get("model_code") if req else None
    page = req.get("page") if req else None
    limit = req.get("limit") if req else None

    result = monitor_service.check_new_trades(model_code, page, limit)

    if result["success"]:
        return {
            "code": 0,
            "msg": "成功",
            "data": result
        }
    else:
        return {
            "code": -1,
            "msg": f"检查失败: {result.get('error')}",
            "data": result
        }


@app.route('/api/monitor/status', methods=["GET"])
@ctrl_handler()
def monitor_status_api(req):
    """获取监控状态接口"""
    status = monitor_service.get_monitor_status()

    return {
        "code": 0,
        "msg": "成功",
        "data": status
    }


# ========== 定时监控控制接口 ==========

@app.route('/api/monitor/scheduler/start', methods=["POST"])
@ctrl_handler()
def start_scheduler_api(req):
    """
    启动定时监控接口

    请求参数:
        interval_seconds: 监控间隔（秒，可选，默认60秒）
    """
    interval_seconds = req.get("interval_seconds") if req else None

    result = scheduler.start(interval_seconds)

    if result["success"]:
        return {
            "code": 0,
            "msg": "成功",
            "data": result
        }
    else:
        return {
            "code": -1,
            "msg": result.get("message"),
            "data": result
        }


@app.route('/api/monitor/scheduler/stop', methods=["POST"])
@ctrl_handler()
def stop_scheduler_api(req):
    """停止定时监控接口"""
    result = scheduler.stop()

    if result["success"]:
        return {
            "code": 0,
            "msg": "成功",
            "data": result
        }
    else:
        return {
            "code": -1,
            "msg": result.get("message"),
            "data": result
        }


@app.route('/api/monitor/scheduler/update_interval', methods=["POST"])
@ctrl_handler()
def update_interval_api(req):
    """
    更新监控间隔接口

    请求参数:
        interval_seconds: 新的监控间隔（秒，必填）
    """
    if not req or "interval_seconds" not in req:
        return {
            "code": -1,
            "msg": "缺少参数: interval_seconds",
            "data": None
        }

    interval_seconds = req.get("interval_seconds")

    result = scheduler.update_interval(interval_seconds)

    if result["success"]:
        return {
            "code": 0,
            "msg": "成功",
            "data": result
        }
    else:
        return {
            "code": -1,
            "msg": result.get("message"),
            "data": result
        }


@app.route('/api/monitor/scheduler/status', methods=["GET"])
@ctrl_handler()
def scheduler_status_api(req):
    """获取调度器状态接口"""
    status = scheduler.get_status()

    return {
        "code": 0,
        "msg": "成功",
        "data": status
    }


# ========== 企业微信推送测试接口 ==========

@app.route('/api/wechat/test', methods=["POST"])
@ctrl_handler()
def test_wechat_api(req):
    """
    测试企业微信推送接口

    请求参数:
        message: 测试消息内容 (可选)
        type: 消息类型 info/warning (可选，默认info)
    """
    try:
        # 检查是否启用企业微信推送
        wechat_enabled = cfg.get_item('WeChat', 'Enabled')
        if wechat_enabled.lower() != 'true':
            return {
                "code": -1,
                "msg": "企业微信推送未启用，请在配置文件中设置 [WeChat] Enabled = true",
                "data": None
            }

        access_token = cfg.get_item('WeChat', 'Access_Token')
        access_name = cfg.get_item('WeChat', 'Access_name')
        at_person = cfg.get_item('WeChat', 'At_person')

        message = req.get("message") if req and "message" in req else "这是一条测试消息"
        msg_type = req.get("type") if req and "type" in req else "info"

        contents = f"> **测试消息**\n> {message}"

        # 根据类型发送不同的消息
        if msg_type == "warning":
            result = wechat_api_warning(
                contents=contents,
                title="企业微信推送测试（告警）",
                access_token=access_token,
                access_name=access_name,
                at_person=at_person
            )
        else:
            result = wechat_api_info(
                contents=contents,
                title="企业微信推送测试（通知）",
                access_token=access_token,
                access_name=access_name,
                at_person=at_person
            )

        if result and result.get('errcode') == 0:
            return {
                "code": 0,
                "msg": "企业微信推送成功",
                "data": result
            }
        else:
            return {
                "code": -1,
                "msg": f"企业微信推送失败: {result.get('errmsg') if result else '未知错误'}",
                "data": result
            }

    except Exception as e:
        route_logger.error(f"测试企业微信推送失败: {str(e)}")
        return {
            "code": -1,
            "msg": f"测试失败: {str(e)}",
            "data": None
        }
