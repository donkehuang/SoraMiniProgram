# 如何让 API Server 公网访问

## 方法1：使用 ngrok（最简单推荐）

### 步骤1：下载安装 ngrok
1. 访问 https://ngrok.com/download
2. 下载 Windows 版本
3. 解压到 `C:\ngrok` 目录

### 步骤2：注册并配置
1. 访问 https://dashboard.ngrok.com/signup 注册账号
2. 登录后，在 Dashboard 页面找到 "Your Authtoken"
3. 复制 token，在命令行运行：
   ```bash
   C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN_HERE
   ```

### 步骤3：启动服务

**终端1 - 启动 API Server：**
```bash
cd C:\Users\donke\Desktop\LuckyTalk\api_server
python sora_api.py
```

**终端2 - 启动 ngrok：**
```bash
C:\ngrok\ngrok.exe http 5000
```

### 步骤4：获取公网URL
ngrok 启动后会显示：
```
Forwarding   https://xxxx-xx-xx.ngrok-free.app -> http://localhost:5000
```

这个 `https://xxxx-xx-xx.ngrok-free.app` 就是你的公网访问地址！

### 步骤5：更新小程序配置
在小程序 `index.js` 中修改 API 地址：
```javascript
const API_BASE = 'https://xxxx-xx-xx.ngrok-free.app';
```

## 方法2：使用 Cloudflare Tunnel（无需注册）

### 步骤1：下载
访问 https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation
下载 cloudflared

### 步骤2：运行
```bash
cloudflared tunnel --url http://localhost:5000
```

会自动生成一个 `*.trycloudflare.com` 的临时域名

## 方法3：localtunnel（最简单，但可能不稳定）

### 前提：需要安装 Node.js

```bash
# 安装
npm install -g localtunnel

# 使用
lt --port 5000
```

会生成类似 `https://random-name.loca.lt` 的URL

## 注意事项

⚠️ **免费内网穿透的限制：**
- ngrok 免费版：每次重启URL会变化，需要更新小程序配置
- 有请求数限制和带宽限制
- 可能有地区访问限制

✅ **生产环境建议：**
- 部署到云服务器（腾讯云、阿里云等）
- 配置固定域名和SSL证书
- 更稳定可靠

## 快速测试命令

创建一个批处理文件 `start_with_ngrok.bat`：
```batch
@echo off
echo 启动 API Server...
start cmd /k "cd /d %~dp0 && python sora_api.py"

timeout /t 3

echo 启动 ngrok...
start cmd /k "C:\ngrok\ngrok.exe http 5000"

echo 完成！请查看 ngrok 窗口获取公网URL
pause
```

运行这个批处理文件即可同时启动服务和内网穿透。
