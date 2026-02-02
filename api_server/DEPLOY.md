# Sora API Server 部署文档

## 📋 目录结构

```
api_server/
├── sora_api.py              # 主程序
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量示例
├── .env                    # 环境变量配置（需创建）
├── .gitignore              # Git 忽略文件
├── deploy.sh               # 自动部署脚本
├── deploy_systemd.sh       # systemd 配置脚本
├── sora-api.service        # systemd 服务文件
├── nginx.conf              # Nginx 配置示例
└── generated_videos/       # 视频存储目录
    └── .gitkeep
```

## 🚀 快速部署（推荐流程）

### 方案A：腾讯云/阿里云部署

#### 1. 购买服务器
- **推荐配置**：2核4G，带宽3M以上
- **系统**：Ubuntu 20.04/22.04 LTS
- **存储**：至少40GB（视频文件会占用空间）

#### 2. 连接到服务器
```bash
ssh root@your_server_ip
```

#### 3. 上传代码
```bash
# 在本地执行
scp -r api_server root@your_server_ip:/var/www/

# 或使用 Git
ssh root@your_server_ip
cd /var/www
git clone https://github.com/donkehuang/SoraMiniProgram.git
cd SoraMiniProgram/api_server
```

#### 4. 运行自动部署脚本
```bash
cd /var/www/SoraMiniProgram/api_server
chmod +x deploy.sh
bash deploy.sh
```

#### 5. 配置环境变量
```bash
cp .env.example .env
nano .env

# 编辑以下内容：
OPENAI_API_KEY=你的OpenAI_API_Key
PORT=5000
FLASK_ENV=production
DEBUG=False
```

#### 6. 测试运行
```bash
source venv/bin/activate
python sora_api.py
```

访问 `http://your_server_ip:5000/api/health` 测试

#### 7. 配置生产环境（Gunicorn + systemd）
```bash
# 配置 systemd 自启动
sudo bash deploy_systemd.sh

# 查看服务状态
sudo systemctl status sora-api

# 查看日志
sudo journalctl -u sora-api -f
```

#### 8. 配置 Nginx 反向代理（可选但推荐）
```bash
# 安装 Nginx
sudo apt-get install nginx

# 复制配置
sudo cp nginx.conf /etc/nginx/sites-available/sora-api
sudo ln -s /etc/nginx/sites-available/sora-api /etc/nginx/sites-enabled/

# 编辑配置，替换域名
sudo nano /etc/nginx/sites-available/sora-api

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 9. 配置 HTTPS（使用 Let's Encrypt）
```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your_domain.com

# 自动续期
sudo certbot renew --dry-run
```

#### 10. 配置防火墙
```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp  # 如果不用 Nginx，需要开放

# 启用防火墙
sudo ufw enable
```

### 方案B：Docker 部署（更简单）

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "600", "sora_api:app"]
```

创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  sora-api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./generated_videos:/app/generated_videos
    env_file:
      - .env
    restart: unless-stopped
```

部署：
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 📝 配置说明

### 环境变量（.env 文件）

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-proj-xxxxx  # 必填

# 服务器配置
PORT=5000
HOST=0.0.0.0

# Flask 配置
FLASK_ENV=production  # 生产环境设为 production
DEBUG=False           # 生产环境设为 False

# 可选：使用代理
# OPENAI_BASE_URL=https://api.openai-proxy.com/v1
```

### 微信小程序配置

部署完成后，需要在微信小程序中配置服务器域名：

1. 登录微信公众平台
2. 进入【开发】→【开发管理】→【开发设置】
3. 在【服务器域名】中添加：
   - **request合法域名**：`https://your_domain.com`
   - **uploadFile合法域名**：`https://your_domain.com`
   - **downloadFile合法域名**：`https://your_domain.com`

4. 修改小程序代码中的 API 地址：
```javascript
// miniprogram/pages/index/index.js
const API_BASE = 'https://your_domain.com';  // 改为你的域名
```

## 🔧 常用命令

### systemd 服务管理
```bash
# 启动服务
sudo systemctl start sora-api

# 停止服务
sudo systemctl stop sora-api

# 重启服务
sudo systemctl restart sora-api

# 查看状态
sudo systemctl status sora-api

# 查看日志
sudo journalctl -u sora-api -f

# 禁用自启动
sudo systemctl disable sora-api
```

### Nginx 管理
```bash
# 测试配置
sudo nginx -t

# 重启
sudo systemctl restart nginx

# 查看日志
sudo tail -f /var/log/nginx/sora-api-access.log
sudo tail -f /var/log/nginx/sora-api-error.log
```

## 🐛 故障排查

### 1. 服务无法启动
```bash
# 查看详细日志
sudo journalctl -u sora-api -n 100

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 手动测试
source venv/bin/activate
python sora_api.py
```

### 2. API 请求失败
```bash
# 测试健康检查
curl http://localhost:5000/api/health

# 测试从外部访问
curl http://your_server_ip:5000/api/health
```

### 3. 视频文件无法访问
```bash
# 检查目录权限
ls -la generated_videos/

# 修改权限
chmod 755 generated_videos/
```

### 4. OpenAI API 超时
- 增加超时时间（已设置为300秒）
- 检查网络连接
- 考虑使用代理

## 📊 性能优化

### 1. Gunicorn 配置
```bash
# 增加 worker 数量（建议 2-4 倍 CPU 核心数）
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 600 sora_api:app

# 使用 gevent 异步 worker
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 --timeout 600 sora_api:app
```

### 2. Nginx 缓存配置
在 nginx.conf 中添加：
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=video_cache:10m max_size=1g inactive=60m;

location /videos/ {
    proxy_cache video_cache;
    proxy_cache_valid 200 1h;
    # ...其他配置
}
```

### 3. 日志轮转
```bash
# 创建 logrotate 配置
sudo nano /etc/logrotate.d/sora-api

# 内容：
/var/log/sora-api/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

## 🔐 安全建议

1. **使用 HTTPS**（必须）
2. **配置防火墙**，只开放必要端口
3. **定期更新系统和依赖**
4. **不要在代码中硬编码 API Key**
5. **设置 API 访问限制**（可使用 Nginx limit_req）
6. **定期备份视频文件和数据库**

## 📈 监控建议

1. **使用 Supervisor 或 systemd 自动重启**
2. **配置日志收集**（ELK、Prometheus等）
3. **设置告警**（服务宕机、磁盘空间不足等）
4. **监控 OpenAI API 使用量**

## 💰 成本估算

- **服务器**：100-300元/月（腾讯云/阿里云）
- **带宽**：按实际使用计费
- **存储**：视频文件可考虑对象存储（COS/OSS）
- **域名**：50-100元/年
- **SSL证书**：Let's Encrypt 免费

## 📞 技术支持

如有问题，请查看：
- 项目 GitHub Issues
- OpenAI API 文档
- Flask 官方文档
