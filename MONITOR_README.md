# 交易监控系统使用说明

## 功能概述

本系统实现了对 https://www.pandaai.online/pandaApi/arena/api/trades 接口的监控功能，支持：
- 手动调用获取交易数据
- 检测新交易
- 定时自动监控
- 灵活的监控间隔设置
- **企业微信推送通知（新增）**

## 安装依赖

```bash
pip install -r requirements.txt
```

如果遇到网络问题，请单独安装：
```bash
pip install requests
pip install APScheduler
```

## 企业微信推送配置

### 1. 配置说明

在 `cfg.ini` 或 `cfg.ini.local` 中配置企业微信机器人：

```ini
[WeChat]
; 企业微信机器人Access Token（从企业微信群机器人设置中获取）
Access_Token = your-webhook-key-here
; 群名称（用于非生产环境标识）
Access_name = Dev_IT_Notification
; @提醒的人（可选，多个人用空格分隔）
At_person =
; 是否启用企业微信推送
Enabled = true
```

### 2. 如何获取 Access Token

1. 在企业微信群中，点击群设置 → 添加群机器人
2. 选择"自定义机器人"
3. 复制 Webhook 地址中的 key 参数值
4. 将 key 值配置到 `Access_Token` 字段

### 3. 推送触发时机

- ✅ 定时监控发现新交易时自动推送
- ✅ 监控任务执行失败时推送告警
- ✅ 可手动调用测试接口验证推送功能

---

## API接口说明

### 1. 获取交易数据

**接口**: `POST /api/monitor/fetch_trades`

**请求参数**:
```json
{
  "model_code": "pandaai",  // 可选，默认pandaai
  "page": 1,                // 可选，默认1
  "limit": 50               // 可选，默认50
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "success": true,
    "data": {
      "code": 200,
      "message": "success",
      "data": [...]
    },
    "check_time": "2025-11-23 18:00:00"
  }
}
```

**使用示例**:
```bash
curl -X POST http://127.0.0.1:5012/api/monitor/fetch_trades \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. 检查新交易

**接口**: `POST /api/monitor/check_new_trades`

**请求参数**: 同上

**响应示例**:
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "success": true,
    "has_new_trades": true,
    "new_trades_count": 2,
    "new_trades": [...],
    "all_data": {...},
    "check_time": "2025-11-23 18:00:00"
  }
}
```

**使用示例**:
```bash
curl -X POST http://127.0.0.1:5012/api/monitor/check_new_trades \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 3. 获取监控状态

**接口**: `GET /api/monitor/status`

**响应示例**:
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "last_check_time": "2025-11-23 18:00:00",
    "has_history_data": true,
    "target_url": "https://www.pandaai.online/pandaApi/arena/api/trades",
    "default_params": {
      "model_code": "pandaai",
      "page": 1,
      "limit": 50
    }
  }
}
```

**使用示例**:
```bash
curl http://127.0.0.1:5012/api/monitor/status
```

---

## 定时监控功能

### 4. 启动定时监控

**接口**: `POST /api/monitor/scheduler/start`

**请求参数**:
```json
{
  "interval_seconds": 60  // 可选，监控间隔秒数，默认60秒
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "success": true,
    "message": "定时监控已启动",
    "interval_seconds": 60,
    "start_time": "2025-11-23 18:00:00"
  }
}
```

**使用示例**:
```bash
# 使用默认间隔（60秒）
curl -X POST http://127.0.0.1:5012/api/monitor/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{}'

# 自定义间隔（30秒）
curl -X POST http://127.0.0.1:5012/api/monitor/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 30}'
```

### 5. 停止定时监控

**接口**: `POST /api/monitor/scheduler/stop`

**响应示例**:
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "success": true,
    "message": "定时监控已停止",
    "stop_time": "2025-11-23 18:10:00"
  }
}
```

**使用示例**:
```bash
curl -X POST http://127.0.0.1:5012/api/monitor/scheduler/stop \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 6. 更新监控间隔

**接口**: `POST /api/monitor/scheduler/update_interval`

**请求参数**:
```json
{
  "interval_seconds": 120  // 必填，新的监控间隔秒数
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "success": true,
    "message": "监控间隔已更新",
    "interval_seconds": 120
  }
}
```

**使用示例**:
```bash
curl -X POST http://127.0.0.1:5012/api/monitor/scheduler/update_interval \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 120}'
```

### 7. 获取调度器状态

**接口**: `GET /api/monitor/scheduler/status`

**响应示例**:
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "is_running": true,
    "interval_seconds": 60,
    "jobs": [
      {
        "id": "trade_monitor_job",
        "name": "交易监控任务",
        "next_run_time": "2025-11-23 18:01:00"
      }
    ]
  }
}
```

**使用示例**:
```bash
curl http://127.0.0.1:5012/api/monitor/scheduler/status
```

---

## 企业微信推送测试

### 8. 测试企业微信推送

**接口**: `POST /api/wechat/test`

**请求参数**:
```json
{
  "message": "测试消息内容",  // 可选，默认"这是一条测试消息"
  "type": "info"             // 可选，info/warning，默认info
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "企业微信推送成功",
  "data": {
    "errcode": 0,
    "errmsg": "ok"
  }
}
```

**使用示例**:
```bash
# 发送测试通知
curl -X POST http://127.0.0.1:5012/api/wechat/test \
  -H "Content-Type: application/json" \
  -d '{"message": "交易监控系统测试", "type": "info"}'

# 发送测试告警
curl -X POST http://127.0.0.1:5012/api/wechat/test \
  -H "Content-Type: application/json" \
  -d '{"message": "这是告警消息", "type": "warning"}'
```

**企业微信推送效果**:

发现新交易时，会自动推送如下格式的消息：
```
交易监控告警
| 2025-11-23 19:30:00

> 发现 2 条新交易
> 检查时间: 2025-11-23 19:30:00

> 1. SC2601 | 开多 | 价格:445.6 | 数量:3.0 | 盈亏:0.00
>    时间: 2025-11-22 01:50:54
> 2. CU2601 | 开空 | 价格:86190.0 | 数量:3.0 | 盈亏:0.00
>    时间: 2025-11-22 00:48:55

> Dev_IT_Notification
```

---

## 配置说明

配置文件位置：
- 生产环境: `cfg.ini`
- 本地开发: `cfg.ini.local`

配置项说明：
```ini
[Monitor]
; 监控目标URL
TargetUrl = https://www.pandaai.online/pandaApi/arena/api/trades
; 默认模型代码
DefaultModelCode = pandaai
; 默认页码
DefaultPage = 1
; 默认每页数量
DefaultLimit = 50
; 定时监控间隔（秒）
DefaultIntervalSeconds = 60
; 是否在启动时自动开启定时监控
AutoStartScheduler = false
```

---

## 使用流程示例

### 场景1：手动检查新交易

```bash
# 1. 启动服务
start_local.bat

# 2. 检查新交易
curl -X POST http://127.0.0.1:5012/api/monitor/check_new_trades \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 场景2：启动定时监控

```bash
# 1. 启动服务
start_local.bat

# 2. 启动定时监控（每30秒检查一次）
curl -X POST http://127.0.0.1:5012/api/monitor/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 30}'

# 3. 查看调度器状态
curl http://127.0.0.1:5012/api/monitor/scheduler/status

# 4. 查看日志（新交易会记录在日志中）
tail -f logs/service.log

# 5. 停止监控
curl -X POST http://127.0.0.1:5012/api/monitor/scheduler/stop \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 日志说明

监控日志记录在 `logs/service.log` 文件中。

当发现新交易时，日志格式如下：
```
2025-11-23 18:00:00 - monitor_scheduler.py[line:30] - INFO: ==================================================
2025-11-23 18:00:00 - monitor_scheduler.py[line:31] - INFO: 开始执行定时监控任务...
2025-11-23 18:00:00 - monitor_scheduler.py[line:38] - INFO: 发现 2 条新交易!
2025-11-23 18:00:00 - monitor_scheduler.py[line:40] - INFO: 新交易: SC2601 | 开多 | 价格: 445.6 | 数量: 3.0 | 盈亏: 0.0 | 时间: 2025-11-22 01:50:54
2025-11-23 18:00:00 - monitor_scheduler.py[line:51] - INFO: 监控任务完成, 检查时间: 2025-11-23 18:00:00
2025-11-23 18:00:00 - monitor_scheduler.py[line:52] - INFO: ==================================================
```

---

## 注意事项

1. 首次调用 `check_new_trades` 不会检测到新交易（因为没有历史数据对比）
2. 定时监控会在后台持续运行，直到调用停止接口或服务重启
3. 监控间隔可以随时调整，无需重启服务
4. 所有监控记录都会输出到日志文件中
5. 建议在生产环境中将 `AutoStartScheduler` 设为 `true`，实现自动监控

---

## 故障排查

### 问题1：无法连接目标接口
- 检查网络连接
- 确认目标URL是否可访问
- 查看日志中的错误信息

### 问题2：定时监控未运行
- 检查调度器状态：`GET /api/monitor/scheduler/status`
- 查看日志中的错误信息
- 确认APScheduler依赖已安装

### 问题3：没有检测到新交易
- 至少调用两次 `check_new_trades` 才能比对出新交易
- 确认目标接口确实有新的交易数据
- 检查交易时间是否比上次检查的更新