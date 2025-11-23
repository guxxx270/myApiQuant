# myApiQuant

基于Flask的API服务框架，从invest-jiurui-function-python项目提取核心结构。

## 项目结构

```
myApiQuant/
├── quier_flask/              # Flask应用核心
│   ├── __init__.py           # Flask应用初始化
│   ├── app_cfg.py            # 配置管理
│   └── route_ctrl.py         # 路由控制和装饰器
├── apps/                     # 业务代码
│   ├── api/                  # API层
│   ├── service/              # 服务层
│   └── utiles/               # 工具类
├── logs/                     # 日志目录
├── run_server.py             # 应用入口
├── cfg.ini                   # 生产配置
├── cfg.ini.local             # 本地配置
├── start_local.bat           # 本地启动脚本
├── start_server.bat          # 生产启动脚本
├── gunicorn.conf.py          # Gunicorn配置
└── requirements.txt          # 依赖列表
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 本地开发

Windows环境：
```bash
start_local.bat
```

或手动启动：
```bash
set USE_LOCAL_CONFIG=true
python run_server.py
```

### 3. 生产部署

使用开发服务器：
```bash
start_server.bat
```

使用Gunicorn（推荐）：
```bash
gunicorn -c gunicorn.conf.py quier_flask:app
```

## 配置说明

### 配置文件

- `cfg.ini.local` - 本地开发配置（127.0.0.1:5012）
- `cfg.ini` - 生产环境配置（0.0.0.0:5012）

### 配置项

```ini
[Service]
Host = 127.0.0.1        # 服务地址
Port = 5012             # 服务端口
LogLevel = 10           # 日志级别 (10-debug, 20-info, 30-warning, 40-error, 50-critical)
```

## API示例

### 健康检查
```bash
GET http://127.0.0.1:5012/hello/testSuccess
```

响应：
```json
{
  "code": 0,
  "data": "ok",
  "msg": "success"
}
```

### 示例API
```bash
POST http://127.0.0.1:5012/api/example
Content-Type: application/json

{
  "test": "data"
}
```

响应：
```json
{
  "code": 0,
  "msg": "成功",
  "data": {
    "message": "这是一个示例API",
    "request": {"test": "data"}
  }
}
```

## 开发指南

### 添加新路由

在 `quier_flask/route_ctrl.py` 中添加：

```python
@app.route('/api/your_endpoint', methods=["POST"])
@ctrl_handler()
def your_api(req):
    """API描述"""
    return {
        "code": 0,
        "msg": "成功",
        "data": {}
    }
```

### API响应格式

标准响应格式：
```json
{
  "code": 0,           // 0-成功, -1-业务错误, 4003-系统异常
  "msg": "成功",
  "data": {}           // 响应数据
}
```

### 日志使用

```python
from quier_flask.route_ctrl import route_logger

route_logger.debug("调试信息")
route_logger.info("普通信息")
route_logger.warning("警告信息")
route_logger.error("错误信息")
```

## 技术栈

- **Web框架**: Flask 2.0.1
- **WSGI服务器**: Gunicorn 20.1.0
- **加密库**: PyCryptodome 3.20.0
- **Python版本**: 3.7+

## 许可证

MIT License
