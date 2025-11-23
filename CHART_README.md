# 盈亏曲线图推送功能说明

## 功能概述

系统支持在推送交易数据时，同时生成并推送盈亏曲线图到企业微信群。

## 功能特性

1. **自动生成盈亏曲线图**
   - 基于所有交易数据计算累计盈亏
   - 绿色区域表示盈利，红色区域表示亏损
   - 显示统计信息：总盈亏、最高点、最低点、交易次数

2. **配置开关控制**
   - 通过配置文件 `EnableChartPush` 开关控制是否推送图表
   - 打开时自动生成并推送，关闭时只推送文本消息

3. **支持多场景**
   - 启动时推送：展示近期交易的盈亏曲线
   - 监控告警推送：发现新交易时推送实时盈亏曲线

## 配置说明

### 1. 启用图表推送

在 `cfg.ini` 或 `cfg.ini.local` 文件的 `[WeChat]` 部分添加：

```ini
[WeChat]
; 企业微信机器人Access Token
Access_Token = your-token-here
; 群名称
Access_name = 研发中心-投研项目组
; 是否启用企业微信推送
Enabled = true
; 是否推送盈亏曲线图（新增）
EnableChartPush = true
```

### 2. 安装依赖

图表推送需要 matplotlib 库，请按以下方式安装：

#### 方法1：使用 pip 直接安装
```bash
pip install matplotlib
```

#### 方法2：使用清华源（国内推荐）
```bash
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 方法3：从 requirements.txt 安装
```bash
pip install -r requirements.txt
```

#### 如果遇到代理问题

如果安装时遇到代理错误，可以尝试：

**Windows命令行：**
```cmd
set HTTP_PROXY=
set HTTPS_PROXY=
pip install matplotlib
```

**Git Bash/Linux:**
```bash
unset HTTP_PROXY
unset HTTPS_PROXY
pip install matplotlib
```

## 使用方法

### 1. 启动时自动推送

当 `EnableChartPush = true` 时，系统启动会：
1. 推送文本消息（包含最近N条交易详情）
2. 自动生成盈亏曲线图
3. 推送图片到企业微信群

### 2. 监控告警推送

当定时监控发现新交易时：
1. 推送告警消息（包含新交易详情）
2. 自动生成累计盈亏曲线图
3. 推送图片到企业微信群

### 3. 关闭图表推送

如果不需要图表，将配置修改为：
```ini
EnableChartPush = false
```

系统将只推送文本消息，不生成图表。

## 图表示例

盈亏曲线图包含以下信息：
- **标题**：显示图表类型和model_code
- **X轴**：交易时间（格式：月-日 时:分）
- **Y轴**：累计盈亏金额
- **曲线**：连接各交易点的累计盈亏曲线
- **填充区域**：盈利区域为绿色，亏损区域为红色
- **统计框**：显示总盈亏、最高点、最低点、交易次数

## 技术说明

1. **图表生成**：使用 matplotlib 库生成高质量图表
2. **图片格式**：PNG格式，150 DPI，尺寸 12x6 英寸
3. **临时文件**：图片生成在系统临时目录，发送后自动清理
4. **字体支持**：自动使用系统中文字体（SimHei/黑体）

## 故障排查

### 问题1：图表未推送

**可能原因：**
- matplotlib 未安装
- EnableChartPush 开关未打开
- 没有交易数据

**解决方法：**
1. 检查日志：`logs/service.log`
2. 查看是否有 "图表生成成功" 或错误信息
3. 确认 matplotlib 已安装：`pip list | grep matplotlib`

### 问题2：图表显示乱码

**可能原因：**
- 系统缺少中文字体

**解决方法：**
- Windows：确保安装了黑体（SimHei）
- Linux：安装中文字体包
  ```bash
  sudo apt-get install fonts-wqy-zenhei
  ```

### 问题3：图表生成失败

**常见错误及解决：**
- `ModuleNotFoundError: No module named 'matplotlib'`
  → 需要安装 matplotlib
- `ValueError: expected list, got NoneType`
  → 检查交易数据是否正常

## 注意事项

1. **图片大小限制**：企业微信对图片大小有限制（一般为2MB），当前配置完全满足要求
2. **性能影响**：生成图表会增加少量CPU和内存开销，对于正常交易量影响可忽略
3. **存储空间**：临时图片会在发送后立即删除，不占用长期存储空间
4. **网络要求**：推送图片需要稳定的网络连接到企业微信服务器

## 开发说明

### 核心模块

1. **apps/utiles/chart_util.py**
   - `generate_pnl_chart()`: 生成盈亏曲线图
   - `cleanup_chart_file()`: 清理临时文件

2. **apps/utiles/wechat_util.py**
   - `wechat_send_image()`: 发送图片到企业微信

3. **配置文件**
   - `cfg.ini` / `cfg.ini.local`
   - 新增 `EnableChartPush` 配置项

### 自定义图表

如需自定义图表样式，可以修改 `chart_util.py` 中的以下参数：
- 图表尺寸：`figsize=(12, 6)`
- 分辨率：`dpi=150`
- 颜色：`line_color`、填充颜色
- 字体大小：`fontsize` 参数
