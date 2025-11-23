# -*- coding:utf-8 -*-
"""
定时监控调度器
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from apps.service.monitor_service import monitor_service
from apps.utiles.wechat_util import wechat_api_info, wechat_api_warning, format_trade_message
from quier_flask import cfg

logger = logging.getLogger("service")


class TradeMonitorScheduler:
    """交易监控定时任务调度器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.job_id = "trade_monitor_job"
        self.check_interval = 60  # 默认60秒检查一次

    def monitor_task(self):
        """监控任务 - 定时执行"""
        try:
            logger.info("=" * 50)
            logger.info("开始执行定时监控任务...")

            result = monitor_service.check_new_trades()

            if result["success"]:
                if result["has_new_trades"]:
                    logger.info(f"发现 {result['new_trades_count']} 条新交易!")

                    # 记录新交易到日志
                    for trade in result["new_trades"]:
                        logger.info(
                            f"新交易: {trade.get('symbol')} | "
                            f"{trade.get('side_code')} | "
                            f"价格: {trade.get('price')} | "
                            f"数量: {trade.get('quantity')} | "
                            f"盈亏: {trade.get('pnl')} | "
                            f"时间: {trade.get('trade_time')}"
                        )

                    # 推送企业微信通知
                    self._send_wechat_notification(result)
                else:
                    logger.info("暂无新交易")

                logger.info(f"监控任务完成, 检查时间: {result['check_time']}")
            else:
                logger.error(f"监控任务失败: {result.get('error')}")
                # 推送失败告警
                self._send_wechat_error(result.get('error'))

            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"监控任务异常: {str(e)}", exc_info=True)
            # 推送异常告警
            self._send_wechat_error(str(e))

    def _send_wechat_notification(self, result):
        """发送企业微信新交易通知"""
        try:
            # 检查是否启用企业微信推送
            wechat_enabled = cfg.get_item('WeChat', 'Enabled')
            if wechat_enabled.lower() != 'true':
                return

            access_token = cfg.get_item('WeChat', 'Access_Token')
            access_name = cfg.get_item('WeChat', 'Access_name')
            at_person = cfg.get_item('WeChat', 'At_person')

            new_trades = result.get('new_trades', [])
            new_trades_count = result.get('new_trades_count', 0)
            check_time = result.get('check_time', '')

            # 格式化消息内容
            contents = f"> **发现 {new_trades_count} 条新交易**\n"
            contents += f"> 检查时间: {check_time}\n\n"
            contents += format_trade_message(new_trades)

            # 发送企业微信通知
            wechat_api_warning(
                contents=contents,
                title="交易监控告警",
                access_token=access_token,
                access_name=access_name,
                at_person=at_person
            )

            logger.info("企业微信新交易通知已发送")

        except Exception as e:
            logger.error(f"发送企业微信通知失败: {str(e)}")

    def _send_wechat_error(self, error_msg):
        """发送企业微信错误告警"""
        try:
            # 检查是否启用企业微信推送
            wechat_enabled = cfg.get_item('WeChat', 'Enabled')
            if wechat_enabled.lower() != 'true':
                return

            access_token = cfg.get_item('WeChat', 'Access_Token')
            access_name = cfg.get_item('WeChat', 'Access_name')
            at_person = cfg.get_item('WeChat', 'At_person')

            # 格式化错误消息
            contents = f"> **监控任务执行失败**\n"
            contents += f"> 错误原因: {error_msg}"

            # 发送企业微信告警
            wechat_api_warning(
                contents=contents,
                title="交易监控异常",
                access_token=access_token,
                access_name=access_name,
                at_person=at_person
            )

            logger.info("企业微信错误告警已发送")

        except Exception as e:
            logger.error(f"发送企业微信错误告警失败: {str(e)}")

    def start(self, interval_seconds=None):
        """
        启动定时监控

        Args:
            interval_seconds: 监控间隔（秒），默认60秒
        """
        if self.is_running:
            logger.warning("定时监控已在运行中")
            return {"success": False, "message": "定时监控已在运行中"}

        if interval_seconds:
            self.check_interval = interval_seconds

        try:
            # 添加定时任务
            self.scheduler.add_job(
                func=self.monitor_task,
                trigger=IntervalTrigger(seconds=self.check_interval),
                id=self.job_id,
                name="交易监控任务",
                replace_existing=True
            )

            # 启动调度器
            self.scheduler.start()
            self.is_running = True

            logger.info(f"定时监控已启动, 间隔: {self.check_interval}秒")

            return {
                "success": True,
                "message": f"定时监控已启动",
                "interval_seconds": self.check_interval,
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            logger.error(f"启动定时监控失败: {str(e)}", exc_info=True)
            return {"success": False, "message": str(e)}

    def stop(self):
        """停止定时监控"""
        if not self.is_running:
            logger.warning("定时监控未在运行")
            return {"success": False, "message": "定时监控未在运行"}

        try:
            self.scheduler.shutdown()
            self.is_running = False

            logger.info("定时监控已停止")

            return {
                "success": True,
                "message": "定时监控已停止",
                "stop_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            logger.error(f"停止定时监控失败: {str(e)}", exc_info=True)
            return {"success": False, "message": str(e)}

    def update_interval(self, interval_seconds):
        """
        更新监控间隔

        Args:
            interval_seconds: 新的监控间隔（秒）
        """
        if not self.is_running:
            self.check_interval = interval_seconds
            return {
                "success": True,
                "message": "监控间隔已更新（需要重新启动才能生效）",
                "interval_seconds": self.check_interval
            }

        try:
            # 重新调度任务
            self.scheduler.reschedule_job(
                job_id=self.job_id,
                trigger=IntervalTrigger(seconds=interval_seconds)
            )

            self.check_interval = interval_seconds

            logger.info(f"监控间隔已更新为: {interval_seconds}秒")

            return {
                "success": True,
                "message": "监控间隔已更新",
                "interval_seconds": self.check_interval
            }

        except Exception as e:
            logger.error(f"更新监控间隔失败: {str(e)}", exc_info=True)
            return {"success": False, "message": str(e)}

    def get_status(self):
        """获取调度器状态"""
        jobs = []
        if self.is_running:
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None
                })

        return {
            "is_running": self.is_running,
            "interval_seconds": self.check_interval,
            "jobs": jobs
        }


# 创建全局调度器实例
scheduler = TradeMonitorScheduler()