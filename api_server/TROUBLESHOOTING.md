# 问题排查指南

## 错误：`Cannot read property 'error' of undefined`

这个错误表示小程序无法正确解析API服务器的响应。请按以下步骤排查：

### 第一步：检查API服务器是否启动

**在新的终端窗口中运行：**

```bash
cd api_server
python sora_api.py
```

你应该看到：
```
 * Serving Flask app 'sora_api'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### 第二步：测试API服务器

**在另一个终端运行测试脚本：**

```bash
cd api_server
pip install requests  # 如果还没有安装
python test_api.py
```

测试脚本会检查：
1. ✅ API服务器是否运行在 http://localhost:5000
2. ✅ 健康检查接口是否正常
3. ✅ 视频生成接口是否可用

### 第三步：检查小程序配置

确保 `miniprogram/pages/index/index.js` 中的API地址正确：

```javascript
apiBaseUrl: 'http://localhost:5000'
```

**重要：** 如果你使用的是真机调试，需要将 `localhost` 改成你电脑的局域网IP地址，例如：
```javascript
apiBaseUrl: 'http://192.168.1.100:5000'  // 替换为你的实际IP
```

查看你的IP地址：
- Windows: `ipconfig`
- Mac/Linux: `ifconfig` 或 `ip addr`

### 第四步：查看API服务器日志

启动API服务器后，当小程序发起请求时，你应该看到类似的日志：

```
[请求] 收到视频生成请求: {'prompt': '...', 'seconds': '12'}
[参数] prompt: 一只可爱的小猫..., seconds: 12
[开始] 开始调用Sora API...
[成功] 视频生成成功，视频ID: xxx
[响应] 返回数据: {...}
```

如果没有看到这些日志，说明小程序的请求没有到达API服务器。

### 第五步：检查微信开发者工具设置

确保以下设置已启用（开发阶段）：

1. **详情 > 本地设置**
   - ✅ 不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书
   - ✅ 不校验远程SSL证书

2. **详情 > 项目配置**
   - 检查 `project.config.json` 中的 `setting.urlCheck` 是否为 `false`

### 第六步：测试网络连接

在微信开发者工具的Console中运行：

```javascript
wx.request({
  url: 'http://localhost:5000/api/health',
  method: 'GET',
  success(res) {
    console.log('API服务器响应:', res)
  },
  fail(err) {
    console.error('请求失败:', err)
  }
})
```

如果成功，你会看到：
```
API服务器响应: {statusCode: 200, data: {status: "ok"}, ...}
```

如果失败，可能是：
- ❌ API服务器未启动
- ❌ 地址配置错误
- ❌ 防火墙阻止连接

### 常见问题

#### Q: API服务器启动失败
```
OSError: [Errno 48] Address already in use
```
**解决：** 端口5000被占用，关闭其他使用5000端口的应用，或修改 `sora_api.py` 中的端口号。

#### Q: OpenAI API密钥错误
```
Error: Incorrect API key provided
```
**解决：** 在 `sora_api.py` 第21行设置正确的API密钥。

#### Q: 真机调试无法连接
**解决：**
1. 确保手机和电脑在同一WiFi网络
2. 使用电脑的局域网IP地址替代 `localhost`
3. 检查电脑防火墙设置

#### Q: 视频生成超时
**解决：** Sora API生成视频可能需要较长时间，可以：
1. 在 `index.js` 中增加超时时间
2. 实现异步轮询机制（获取videoId后轮询检查状态）

### 完整测试流程

```bash
# 1. 启动API服务器
cd api_server
python sora_api.py

# 2. 在另一个终端测试API
python test_api.py

# 3. 确认测试通过后，在微信开发者工具中打开小程序
# 4. 点击"生成视频"按钮
```

### 获取更多帮助

如果以上步骤都无法解决问题，请提供：
1. API服务器的完整日志输出
2. 小程序Console的错误信息
3. `test_api.py` 的测试结果
4. 你使用的设备（模拟器/真机）
