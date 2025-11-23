# -*- coding:utf-8 -*-
"""
企业微信推送工具
"""
import datetime
import json
import logging
import requests

logger = logging.getLogger("service")


def wechat_api_middle(contents, access_token, access_name='', at_person=''):
    """
    企业微信推送中间层

    Args:
        contents: 推送内容
        access_token: 企业微信机器人Token
        access_name: 群名称（用于非生产环境标识）
        at_person: @提醒的人
    """
    try:
        headers = {'Content-Type': 'application/json'}
        api_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={access_token}"

        contents = '\n'.join(contents.split('\n'))

        # 开发环境内容拼接对应群名
        if access_name and 'Prod' not in access_name:
            contents = contents + '\n > ' + access_name

        # At到人
        if at_person:
            contents = contents + '\n > ' + at_person

        json_text = {
            'msgtype': 'markdown',
            'markdown': {
                'content': f"{contents}"
            }
        }

        # 不使用代理
        proxies = {
            "http": None,
            "https": None
        }

        response = requests.post(api_url, data=json.dumps(json_text), headers=headers, timeout=10, proxies=proxies)
        response.raise_for_status()

        result = response.json()
        if result.get('errcode') == 0:
            logger.info(f"企业微信推送成功")
        else:
            logger.error(f"企业微信推送失败: {result}")

        return result

    except Exception as e:
        logger.error(f'企业微信推送异常: {str(e)}')
        return {"errcode": -1, "errmsg": str(e)}


def wechat_api_warning(contents, title="告警", access_token=None, access_name='', at_person=''):
    """
    发送告警信息

    Args:
        contents: 信息详情
        title: 标题
        access_token: 企业微信机器人Token
        access_name: 群名称
        at_person: @提醒的人

    Example:
        wechat_api_warning(
            contents="> 发现3条新交易",
            title="交易监控告警",
            access_token="your-token-here"
        )
    """
    if not access_token:
        logger.warning("企业微信Token未配置，跳过推送")
        return

    msg = f"""# <font color='warning'>**{title}**</font>
              > <font color='comment'>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>
              {contents}"""

    return wechat_api_middle(msg, access_token, access_name, at_person)


def wechat_api_info(contents, title="通知", access_token=None, access_name='', at_person=''):
    """
    发送通知信息

    Args:
        contents: 信息详情
        title: 标题
        access_token: 企业微信机器人Token
        access_name: 群名称
        at_person: @提醒的人

    Example:
        wechat_api_info(
            contents="> 监控启动成功",
            title="交易监控通知",
            access_token="your-token-here"
        )
    """
    if not access_token:
        logger.warning("企业微信Token未配置，跳过推送")
        return

    msg = f"""# <font color='info'>**{title}**</font>
              > <font color='comment'>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>
              {contents}"""

    return wechat_api_middle(msg, access_token, access_name, at_person)


def format_trade_message(trades):
    """
    格式化交易信息为企业微信消息

    Args:
        trades: 交易列表

    Returns:
        str: 格式化后的消息内容
    """
    if not trades:
        return "> 暂无交易数据"

    contents = ""
    for i, trade in enumerate(trades[:10], 1):  # 最多显示10条
        symbol = trade.get('symbol', 'N/A')
        side_code = trade.get('side_code', 'N/A')
        side_display = side_code
        if side_code == '开多':
            side_display = "<font color='red'>开多</font>"
        elif side_code == '开空':
            side_display = "<font color='green'>开空</font>"
        price = trade.get('price', 0)
        quantity = trade.get('quantity', 0)
        pnl = trade.get('pnl', 0)
        trade_time = trade.get('trade_time', 'N/A')

        contents += f"> {i}. **{symbol}** | {side_display} | 价格:{price} | 数量:{quantity} | 盈亏:{pnl:.2f}\n"
        contents += f">    时间: {trade_time}\n"

    if len(trades) > 10:
        contents += f"\n> 还有 {len(trades) - 10} 条交易未显示..."

    return contents
