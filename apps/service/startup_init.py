# -*- coding:utf-8 -*-
"""
应用启动初始化模块
"""
import logging
from apps.service.monitor_service import monitor_service
from apps.service.monitor_scheduler import scheduler
from apps.utiles.wechat_util import wechat_api_info, format_trade_message
from quier_flask import cfg

logger = logging.getLogger("service")


def startup_push_recent_trades():
    """
    启动时推送最近的交易记录（循环所有model_codes）
    """
    try:
        # 检查是否启用启动推送
        try:
            auto_push = cfg.get_item('Monitor', 'AutoPushOnStartup')
            if auto_push.lower() != 'true':
                logger.info("启动时推送已禁用")
                return
        except Exception:
            logger.info("未配置AutoPushOnStartup，跳过启动推送")
            return

        # 检查企业微信是否启用
        try:
            wechat_enabled = cfg.get_item('WeChat', 'Enabled')
            if wechat_enabled.lower() != 'true':
                logger.warning("企业微信推送未启用，跳过启动推送")
                return
        except Exception:
            logger.warning("未配置企业微信，跳过启动推送")
            return

        # 获取推送条数配置
        try:
            push_count = int(cfg.get_item('Monitor', 'StartupPushCount'))
        except Exception:
            push_count = 5
            logger.info(f"未配置StartupPushCount，使用默认值: {push_count}")

        logger.info("=" * 50)
        logger.info("开始执行启动时交易推送...")

        # 获取所有需要监控的model_codes
        model_codes = monitor_service.get_model_codes()
        logger.info(f"待推送的model_codes: {model_codes}")

        # 获取企业微信配置
        access_token = cfg.get_item('WeChat', 'Access_Token')
        access_name = cfg.get_item('WeChat', 'Access_name')
        at_person = cfg.get_item('WeChat', 'At_person')

        # 循环每个model_code
        for model_code in model_codes:
            logger.info(f"开始处理 model_code: {model_code}")

            # 获取交易数据
            result = monitor_service.fetch_trades(model_code=model_code)

            if not result["success"]:
                logger.error(f"[{model_code}] 获取交易数据失败: {result.get('error')}")
                continue

            # 提取交易列表
            data = result.get("data", {})
            trades_data = data.get("data", [])

            if not trades_data or len(trades_data) == 0:
                logger.warning(f"[{model_code}] 没有交易数据")
                continue

            trades = trades_data[0].get("trades", [])

            if not trades or len(trades) == 0:
                logger.warning(f"[{model_code}] 没有交易记录")
                continue

            # 取最近N条交易
            recent_trades = trades[:push_count]
            actual_count = len(recent_trades)

            logger.info(f"[{model_code}] 获取到 {len(trades)} 条交易，准备推送最近 {actual_count} 条")

            # 格式化推送消息
            contents = f"> **交易监控系统已启动**\n"
            contents += f"> Model Code: {model_code}\n"
            contents += f"> 检查时间: {result.get('check_time')}\n"
            contents += f"> 共获取到 {len(trades)} 条交易记录\n\n"
            contents += f"> **最近 {actual_count} 条交易：**\n\n"
            contents += format_trade_message(recent_trades)

            # 发送企业微信通知，标题带上model_code
            wechat_api_info(
                contents=contents,
                title=f"25届期货模拟交易大赛AI各模型启动 [{model_code}]",
                access_token=access_token,
                access_name=access_name,
                at_person=at_person
            )

            logger.info(f"[{model_code}] 启动推送完成，已推送 {actual_count} 条交易")

        logger.info("所有model_code的启动推送完成")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"启动推送异常: {str(e)}", exc_info=True)


def startup_auto_monitor():
    """
    启动时自动开启定时监控
    """
    try:
        # 检查是否启用自动监控
        try:
            auto_start = cfg.get_item('Monitor', 'AutoStartScheduler')
            if auto_start.lower() != 'true':
                logger.info("自动启动监控已禁用")
                return
        except Exception:
            logger.info("未配置AutoStartScheduler，跳过自动监控")
            return

        # 获取监控间隔
        try:
            interval_seconds = int(cfg.get_item('Monitor', 'DefaultIntervalSeconds'))
        except Exception:
            interval_seconds = 60
            logger.info(f"未配置DefaultIntervalSeconds，使用默认值: {interval_seconds}秒")

        logger.info("=" * 50)
        logger.info("开始启动定时监控...")

        # 启动定时监控
        result = scheduler.start(interval_seconds)

        if result["success"]:
            logger.info(f"定时监控已自动启动，间隔: {interval_seconds}秒")
        else:
            logger.error(f"定时监控启动失败: {result.get('message')}")

        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"启动监控异常: {str(e)}", exc_info=True)


def init_app_startup():
    """
    应用启动时的初始化函数
    """
    logger.info("=" * 50)
    logger.info("开始执行应用启动初始化...")
    logger.info("=" * 50)

    # 1. 启动时推送最近的交易
    startup_push_recent_trades()

    # 2. 启动定时监控
    startup_auto_monitor()

    logger.info("=" * 50)
    logger.info("应用启动初始化完成")
    logger.info("=" * 50)