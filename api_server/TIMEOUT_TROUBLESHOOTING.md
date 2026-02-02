# OpenAI API超时问题排查指南

## 问题描述

```
[警告] 视频创建失败 (尝试 1/3): Request timed out.
[警告] 视频创建失败 (尝试 2/3): Request timed out.
[警告] 视频创建失败 (尝试 3/3): Request timed out.
[失败] 视频创建失败: Request timed out.
```

## 🔍 快速诊断

### 步骤1：运行连接测试

```bash
cd api_server
python test_openai_connection.py
```

这个测试会：
1. ✅ 验证API密钥是否有效
2. ✅ 测试网络连接
3. ✅ 测试创建视频任务

### 步骤2：检查网络连接

测试代理服务器是否可达：

```bash
# Windows
ping api.openai-proxy.com

# Mac/Linux
ping api.openai-proxy.com
```

**正常情况：** 应该能ping通，延迟在合理范围内。

### 步骤3：测试端口连接

```bash
# Windows (PowerShell)
Test-NetConnection -ComputerName api.openai-proxy.com -Port 443

# Mac/Linux
nc -zv api.openai-proxy.com 443
```

---

## 🛠️ 解决方案

### 方案1：增加超时时间（已应用）✅

已在代码中设置：
```python
client = OpenAI(
    timeout=300.0,  # 5分钟超时
    max_retries=3
)
```

### 方案2：使用官方OpenAI API

如果代理不稳定，可以切换到官方API：

```python
client = OpenAI(
    api_key='你的官方API密钥',
    timeout=300.0,
    max_retries=3,
    # 不设置base_url，使用默认的官方API
)
```

**注意：** 官方API需要使用官方的API密钥。

### 方案3：使用系统代理

如果你使用VPN或代理，可以配置：

```python
import os

# 设置代理
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'

client = OpenAI(
    api_key='your-api-key',
    timeout=300.0
)
```

### 方案4：检查代理服务状态

你使用的代理 `https://api.openai-proxy.com/v1` 可能：
- 服务器过载
- 正在维护
- 网络路由问题

**建议：**
1. 联系代理服务提供商
2. 查看服务状态页面
3. 尝试其他代理服务

---

## 📊 常见超时原因

### 1. 网络问题

**症状：** 所有API请求都超时
**解决：**
- 检查网络连接
- 重启路由器
- 尝试切换网络（WiFi/移动网络）

### 2. 代理问题

**症状：** 只有OpenAI API超时，其他网站正常
**解决：**
- 检查代理服务状态
- 切换到官方API
- 联系代理提供商

### 3. API服务器问题

**症状：** 偶尔超时，有时正常
**解决：**
- 等待一段时间后重试
- 检查OpenAI服务状态
- 增加重试次数

### 4. 防火墙/杀毒软件

**症状：** 刚开始正常，逐渐变慢直到超时
**解决：**
- 暂时关闭防火墙测试
- 添加API域名到白名单
- 检查杀毒软件设置

---

## 🧪 调试技巧

### 1. 启用详细日志

```python
import logging

# 启用OpenAI调试日志
logging.basicConfig(level=logging.DEBUG)

client = OpenAI(
    api_key='your-key',
    timeout=300.0
)
```

### 2. 分步测试

先测试简单的API：
```python
# 测试1：简单文本生成
response = client.responses.create(
    model="gpt-4o-mini",
    input="Hello"
)

# 测试2：图像生成
image = client.images.generate(
    model="gpt-image-1.5",
    prompt="A cat"
)

# 测试3：视频创建
video = client.videos.create(
    model="sora-2",
    prompt="A cat"
)
```

如果测试1和2成功，测试3超时，可能是视频API特有问题。

### 3. 使用curl测试

```bash
curl -X POST https://api.openai-proxy.com/v1/videos \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A cat","model":"sora-2","seconds":"8","size":"720x1280"}'
```

---

## 📝 日志分析

### 正常的日志

```
[请求] 收到视频生成请求
[参数] prompt: ..., seconds: 8
[开始] 开始调用Sora API...
[创建] 视频任务创建成功，视频ID: video_xxx
```

### 超时的日志

```
[请求] 收到视频生成请求
[参数] prompt: ..., seconds: 8
[开始] 开始调用Sora API...
INFO - Retrying request to /videos in 0.456775 seconds
[警告] 视频创建失败 (尝试 1/3): Request timed out.
```

### 网络错误的日志

```
ConnectionError: Error communicating with OpenAI
```

---

## ✅ 检查清单

在尝试以下操作前，请确认：

- [ ] API服务器已重启（修改代码后）
- [ ] 网络连接正常
- [ ] 可以ping通 `api.openai-proxy.com`
- [ ] API密钥有效（可以创建简单的文本）
- [ ] 防火墙未阻止Python进程
- [ ] 代理服务正常运行

---

## 🚀 建议的操作顺序

### 第1步：运行测试脚本
```bash
python test_openai_connection.py
```

### 第2步：根据测试结果操作

**如果测试1失败：**
- 检查网络连接
- 检查API密钥
- 检查代理设置

**如果测试1成功，测试2超时：**
- 等待一段时间后重试
- 联系代理服务提供商
- 考虑切换到官方API

**如果两个测试都成功：**
- 重启API服务器
- 重试生成视频

---

## 📞 获取帮助

如果以上方案都无法解决，请提供：

1. `test_openai_connection.py` 的完整输出
2. `ping api.openai-proxy.com` 的结果
3. API服务器的完整日志
4. 你的网络环境（家庭网络/公司网络/VPN）

---

## 💡 预防措施

为了避免将来再次出现超时：

1. **监控API状态** - 定期检查服务是否正常
2. **使用重试机制** - 已在代码中实现（3次重试）
3. **增加超时时间** - 已设置为5分钟
4. **备用API服务** - 准备多个API端点
5. **网络优化** - 使用稳定的网络环境

---

## 🎯 当前已应用的修复

✅ 超时时间从默认增加到5分钟
✅ 最大重试次数设置为3次
✅ 配置了代理API地址
✅ 添加了详细的配置日志

---

## 🔄 重启并测试

修改代码后，**必须重启API服务器**：

```bash
# 停止旧服务 (Ctrl+C)
cd api_server
python sora_api.py
```

然后运行测试脚本：
```bash
python test_openai_connection.py
```

---

## 📌 下一步

运行 `test_openai_connection.py` 后，将结果告诉我，我会根据具体情况提供针对性的解决方案。
