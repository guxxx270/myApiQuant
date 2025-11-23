# -*- coding:utf-8 -*-
"""
图表生成工具
"""
import os
import logging
import tempfile
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

logger = logging.getLogger("service")

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def generate_pnl_chart(trades, model_code, chart_title="盈亏曲线图"):
    """
    生成盈亏曲线图

    Args:
        trades: 交易数据列表
        model_code: 模型代码
        chart_title: 图表标题

    Returns:
        str: 图片文件路径，如果生成失败返回None
    """
    try:
        if not trades or len(trades) == 0:
            logger.warning(f"[{model_code}] 没有交易数据，无法生成图表")
            return None

        # 提取数据
        trade_times = []
        cumulative_pnl = []
        cumsum = 0

        for trade in trades:
            try:
                # 解析交易时间
                trade_time_str = trade.get('trade_time', '')
                if trade_time_str:
                    trade_time = datetime.strptime(trade_time_str, '%Y-%m-%d %H:%M:%S')
                    trade_times.append(trade_time)

                    # 累计盈亏
                    pnl = float(trade.get('pnl', 0))
                    cumsum += pnl
                    cumulative_pnl.append(cumsum)
            except Exception as e:
                logger.error(f"处理交易数据失败: {str(e)}")
                continue

        if not trade_times or not cumulative_pnl:
            logger.warning(f"[{model_code}] 没有有效的交易数据")
            return None

        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 6))

        # 绘制盈亏曲线
        line_color = '#00C853' if cumulative_pnl[-1] >= 0 else '#FF1744'
        ax.plot(trade_times, cumulative_pnl,
                marker='o', linewidth=2, markersize=4,
                color=line_color, label='累计盈亏')

        # 添加零线
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

        # 填充区域
        ax.fill_between(trade_times, cumulative_pnl, 0,
                        where=[y >= 0 for y in cumulative_pnl],
                        interpolate=True, alpha=0.3, color='#00C853')
        ax.fill_between(trade_times, cumulative_pnl, 0,
                        where=[y < 0 for y in cumulative_pnl],
                        interpolate=True, alpha=0.3, color='#FF1744')

        # 设置标题和标签
        ax.set_title(f'{chart_title} [{model_code}]',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('交易时间', fontsize=12)
        ax.set_ylabel('累计盈亏', fontsize=12)

        # 格式化x轴日期
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.xticks(rotation=45, ha='right')

        # 添加网格
        ax.grid(True, alpha=0.3, linestyle='--')

        # 添加统计信息
        total_pnl = cumulative_pnl[-1]
        max_pnl = max(cumulative_pnl)
        min_pnl = min(cumulative_pnl)
        trade_count = len(trades)

        stats_text = f'总盈亏: {total_pnl:.2f}\n'
        stats_text += f'最高: {max_pnl:.2f}\n'
        stats_text += f'最低: {min_pnl:.2f}\n'
        stats_text += f'交易次数: {trade_count}'

        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # 调整布局
        plt.tight_layout()

        # 保存图片到临时文件
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pnl_chart_{model_code}_{timestamp}.png'
        filepath = os.path.join(temp_dir, filename)

        plt.savefig(filepath, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)

        logger.info(f"[{model_code}] 图表生成成功: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"[{model_code}] 生成图表失败: {str(e)}", exc_info=True)
        return None


def cleanup_chart_file(filepath):
    """
    清理图表文件

    Args:
        filepath: 图片文件路径
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"清理图表文件: {filepath}")
    except Exception as e:
        logger.error(f"清理图表文件失败: {str(e)}")
