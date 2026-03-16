#!/bin/bash

# 配置 Nginx HTTPS 并更新服务

echo "=========================================="
echo "配置 Nginx HTTPS 并更新服务"
echo "=========================================="

DOMAIN="www.enfuri51.xyz"
EMAIL="m13236533199@163.com"
NGINX_CONF="/etc/nginx/sites-available/sora-api"
WORK_DIR="/home/admin/SoraMiniProgram/api_server"

# 检查证书是否存在，如果不存在则申请
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "⚠️ SSL 证书不存在，开始申请证书..."
    echo "=========================================="

    # 检查是否安装了 certbot
    if ! command -v certbot &> /dev/null; then
        echo "📦 安装 Certbot..."
        sudo apt-get update
        sudo apt-get install -y certbot
    fi

    # 临时启动 Nginx（如果未运行）
    if ! systemctl is-active --quiet nginx; then
        echo "🚀 临时启动 Nginx 用于证书验证..."
        sudo systemctl start nginx
    fi

    # 申请证书
    echo "🔐 申请 SSL 证书..."
    sudo certbot certonly --webroot -w /var/www/html -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

    if [ $? -eq 0 ]; then
        echo "✅ SSL 证书申请成功"
    else
        echo "❌ SSL 证书申请失败"
        echo "请检查:"
        echo "  1. 域名 $DOMAIN 是否正确解析到服务器"
        echo "  2. 80端口是否开放"
        echo "  3. Nginx是否正常运行"
        exit 1
    fi
fi

echo "✅ SSL 证书已找到"

# 进入工作目录
cd "$WORK_DIR" || exit 1

# 拉取最新代码
echo ""
echo "=========================================="
echo "拉取最新代码"
echo "=========================================="
git pull origin master
if [ $? -ne 0 ]; then
    echo "⚠️ Git拉取失败,继续使用现有代码..."
else
    echo "✅ 代码拉取成功"
fi

# 备份现有配置
if [ -f "$NGINX_CONF" ]; then
    echo "📦 备份现有配置..."
    sudo cp "$NGINX_CONF" "${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 创建配置目录（如果不存在）
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# 复制配置文件
echo "📝 配置 Nginx..."
sudo cp nginx-https.conf "$NGINX_CONF"

# 启用配置
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/sora-api

# 删除默认配置（可选）
# sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
echo "🧪 测试 Nginx 配置..."
if sudo nginx -t; then
    echo "✅ Nginx 配置测试通过"
else
    echo "❌ Nginx 配置测试失败"
    exit 1
fi

# 重启 Nginx
echo "🔄 重启 Nginx..."
sudo systemctl restart nginx

if [ $? -eq 0 ]; then
    echo "✅ Nginx 重启成功"
else
    echo "❌ Nginx 重启失败"
    exit 1
fi

# 更新 Flask API 服务
echo ""
echo "=========================================="
echo "更新 Flask API 服务"
echo "=========================================="

# 停止现有服务
echo "🛑 停止现有 Flask 服务..."
pkill -f sora_api.py
sleep 2

# 启动新服务
echo "🚀 启动新的 Flask 服务..."
source venv/bin/activate
nohup python sora_api.py > server.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务状态
echo "📊 检查服务状态..."
ps aux | grep sora_api.py | grep -v grep

if [ $? -eq 0 ]; then
    echo "✅ Flask API 服务运行正常"
else
    echo "❌ Flask API 服务启动失败"
    echo "查看日志:"
    tail -n 20 server.log
    exit 1
fi

# 验证 HTTPS
echo ""
echo "=========================================="
echo "验证 HTTPS 访问"
echo "=========================================="
curl -I https://$DOMAIN/api/health

echo ""
echo "=========================================="
echo "✅ 更新完成！"
echo "=========================================="
echo "API 地址: https://$DOMAIN"
echo "视频地址: https://$DOMAIN/videos/"
echo ""
echo "查看日志: tail -f $WORK_DIR/server.log"
echo "=========================================="
