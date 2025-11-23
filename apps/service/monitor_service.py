# -*- coding:utf-8 -*-
"""
交易接口监控服务
"""
import requests
import logging
import json
from datetime import datetime
from quier_flask import cfg

logger = logging.getLogger("service")


class TradeMonitorService:
    """交易监控服务类"""

    def __init__(self):
        self.target_url = "https://www.pandaai.online/pandaApi/arena/api/trades"
        self.default_params = {
            "page": 1,
            "limit": 50
        }
        # 改为字典，按model_code存储最后的数据
        self.last_data = {}
        # 改为字典，按model_code存储最后的检查时间
        self.last_check_time = {}

    def get_model_codes(self):
        """
        从配置文件获取model_codes列表

        Returns:
            list: model_code列表
        """
        try:
            model_codes_str = cfg.get_item('Monitor', 'ModelCodes')
        except Exception:
            # 如果配置不存在，默认使用pandaai
            model_codes_str = 'pandaai'

        return [code.strip() for code in model_codes_str.split(',')]

    def fetch_trades(self, model_code, page=None, limit=None):
        """
        获取交易数据

        Args:
            model_code: 模型代码（必填）
            page: 页码
            limit: 每页数量

        Returns:
            dict: 接口返回数据
        """
        if not model_code:
            return {
                "success": False,
                "error": "model_code is required",
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        params = {
            "model_code": model_code,
            "page": page or self.default_params["page"],
            "limit": limit or self.default_params["limit"]
        }

        try:
            logger.info(f"开始请求交易数据: {params}")
            # 不使用代理
            proxies = {
                "http": None,
                "https": None
            }
            response = requests.get(self.target_url, params=params, timeout=10, proxies=proxies)
            response.raise_for_status()

            data = response.json()
            logger.info(f"成功获取交易数据, 返回码: {data.get('code')}")

            # 更新该model_code的最后检查时间
            check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_check_time[model_code] = check_time

            return {
                "success": True,
                "model_code": model_code,
                "data": data,
                "check_time": check_time
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"请求交易数据失败: {str(e)}")
            return {
                "success": False,
                "model_code": model_code,
                "error": str(e),
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"处理交易数据失败: {str(e)}")
            return {
                "success": False,
                "model_code": model_code,
                "error": str(e),
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def check_new_trades(self, model_code, page=None, limit=None):
        """
        检查是否有新交易

        Args:
            model_code: 模型代码（必填）
            page: 页码
            limit: 每页数量

        Returns:
            dict: 包含是否有新交易和新交易数据
        """
        result = self.fetch_trades(model_code, page, limit)

        if not result["success"]:
            return result

        current_data = result["data"]
        has_new = False
        new_trades = []

        # 如果有该model_code的历史数据，则比对
        if model_code in self.last_data:
            try:
                old_trades = self.last_data[model_code].get("data", [{}])[0].get("trades", [])
                new_trades_list = current_data.get("data", [{}])[0].get("trades", [])

                # 获取旧数据中最新的交易时间
                if old_trades:
                    last_trade_time = old_trades[0].get("trade_time")

                    # 筛选出比上次检查时间更新的交易
                    for trade in new_trades_list:
                        if trade.get("trade_time") > last_trade_time:
                            new_trades.append(trade)
                            has_new = True

                logger.info(f"[{model_code}] 发现 {len(new_trades)} 条新交易")

            except Exception as e:
                logger.error(f"[{model_code}] 比对交易数据失败: {str(e)}")

        # 更新该model_code的历史数据
        self.last_data[model_code] = current_data

        return {
            "success": True,
            "model_code": model_code,
            "has_new_trades": has_new,
            "new_trades_count": len(new_trades),
            "new_trades": new_trades,
            "all_data": current_data,
            "check_time": result["check_time"]
        }

    def get_monitor_status(self):
        """
        获取监控状态

        Returns:
            dict: 监控状态信息
        """
        return {
            "last_check_time": self.last_check_time,
            "has_history_data": len(self.last_data) > 0,
            "monitored_model_codes": list(self.last_data.keys()),
            "target_url": self.target_url,
            "default_params": self.default_params
        }


# 创建全局服务实例
monitor_service = TradeMonitorService()