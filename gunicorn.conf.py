# -*- coding:utf-8 -*-
"""Gunicorn配置文件"""

# 工作进程数量
workers = 3

# 工作模式
worker_class = "sync"

# 等待队列最大长度
backlog = 128

# 绑定地址
bind = "0.0.0.0:5012"

# 错误日志文件
errorlog = "logs/gunicorn_error.log"

# 访问日志文件
accesslog = "logs/gunicorn_access.log"

# 日志级别
loglevel = 'info'

# 超时时间（秒）
timeout = 120

# 优雅重启超时时间
graceful_timeout = 30

# 保持连接时间
keepalive = 5
