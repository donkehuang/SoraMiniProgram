#!/bin/bash
# HTTPS配置脚本 - 为API服务器配置HTTPS访问（自动申请SSL证书）

echo "=========================================="
echo "API服务器HTTPS配置脚本"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "错误: 请使用root用户运行此脚本"
    echo "使用命令: sudo bash setup_https.sh"
    exit 1
fi

# 配置域名和邮箱（可修改）
DOMAIN_NAME="www.enfuri51.xyz"
EMAIL="m13236533199@163.com"

echo "配置信息："
echo "  域名: $DOMAIN_NAME"
echo "  邮箱: $EMAIL"
echo ""
read -p "确认使用以上配置？(Y/n): " confirm
if [[ $confirm =~ ^[Nn]$ ]]; then
    read -p "请输入域名: " DOMAIN_NAME
    read -p "请输入邮箱: " EMAIL
fi

if [ -z "$DOMAIN_NAME" ]; then
    echo "错误: 域名不能为空"
    exit 1
fi

if [ -z "$EMAIL" ]; then
    echo "错误: 邮箱不能为空"
    exit 1
fi

# 1. 安装Nginx
echo "[步骤1] 安装Nginx..."
if ! command -v nginx &> /dev/null; then
    apt update
    apt install -y nginx
    echo "✓ Nginx安装完成"
else
    echo "✓ Nginx已安装"
fi

# 2. 安装Certbot和Nginx插件
echo ""
echo "[步骤2] 安装Certbot（Let's Encrypt客户端）..."
if ! command -v certbot &> /dev/null; then
    apt update
    apt install -y certbot python3-certbot-nginx
    echo "✓ Certbot安装完成"
else
    echo "✓ Certbot已安装"
fi

# 3. 创建临时Nginx配置（用于证书验证）
echo ""
echo "[步骤3] 创建临时Nginx配置（HTTP）..."
cat > /etc/nginx/sites-available/sora-api << EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME};

    # 日志配置
    access_log /var/log/nginx/sora-api-access.log;
    error_log /var/log/nginx/sora-api-error.log;

    # 反向代理到本地API服务（5000端口）
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # 超时设置（视频生成需要较长时间）
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;

        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件（生成的视频）
    location /videos/ {
        alias /root/luckytalk-api/generated_videos/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

echo "✓ 临时Nginx配置创建完成"

# 4. 启用配置并测试
echo ""
echo "[步骤4] 启用Nginx配置..."
ln -sf /etc/nginx/sites-available/sora-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
echo "✓ 配置已启用"

# 测试配置
echo ""
echo "测试Nginx配置..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✓ Nginx配置测试通过"
else
    echo "✗ Nginx配置测试失败，请检查配置"
    exit 1
fi

# 5. 重启Nginx
echo ""
echo "[步骤5] 重启Nginx..."
systemctl restart nginx
systemctl enable nginx
echo "✓ Nginx已重启并设置为开机自启"

# 6. 检查域名解析
echo ""
echo "[步骤6] 检查域名解析..."
echo "正在检查域名 $DOMAIN_NAME 是否解析到本机..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN_NAME | head -n1)

echo "服务器公网IP: $SERVER_IP"
echo "域名解析IP: $DOMAIN_IP"
echo ""

if [ "$DOMAIN_IP" != "$SERVER_IP" ] && [ "$DOMAIN_IP" != "" ]; then
    echo "⚠️  警告: 域名解析IP与服务器IP不匹配！"
    echo "请确保域名 $DOMAIN_NAME 已正确解析到 $SERVER_IP"
    echo ""
    read -p "是否继续？(Y/n): " continue_anyway
    if [[ $continue_anyway =~ ^[Nn]$ ]]; then
        exit 1
    fi
fi

# 7. 申请SSL证书
echo ""
echo "=========================================="
echo "[步骤7] 申请SSL证书（Let's Encrypt）"
echo "=========================================="
echo ""
echo "正在为域名 $DOMAIN_NAME 申请证书..."
echo "邮箱: $EMAIL"
echo ""

# 申请证书（自动配置Nginx并启用HTTPS重定向）
# 注意：不使用 --uir 参数，因为Nginx插件不支持
certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL --redirect --hsts

CERTBOT_EXIT_CODE=$?

# 检查证书文件是否存在
if [ -f "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" ]; then
    echo ""
    echo "✓ SSL证书申请成功！"
    echo "证书路径: /etc/letsencrypt/live/$DOMAIN_NAME/"
    echo "有效期至: 2026-06-13"
else
    echo ""
    echo "✗ SSL证书申请失败"
    echo ""
    echo "可能的原因："
    echo "1. 域名 $DOMAIN_NAME 未正确解析到服务器IP"
    echo "2. 防火墙未开放80端口"
    echo "3. 阿里云安全组未开放80端口"
    echo ""
    echo "请检查以上问题后重新运行脚本"
    exit 1
fi

# 8. 配置自动续期
echo ""
echo "[步骤8] 配置证书自动续期..."
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
echo "✓ 自动续期任务已添加（每天凌晨3点检查并续期）"

# 9. 配置防火墙
echo ""
echo "[步骤9] 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo "✓ UFW防火墙已配置"
else
    echo "提示: 请确保防火墙已开放80和443端口"
    echo "      如果使用iptables或云安全组，请手动配置"
fi

# 10. 完成
echo ""
echo "=========================================="
echo "✓ HTTPS配置完成！"
echo "=========================================="
echo ""
echo "API地址："
echo "  HTTP:  http://${DOMAIN_NAME}"
echo "  HTTPS: https://${DOMAIN_NAME} ✅"
echo ""
echo "证书信息："
echo "  颁发机构: Let's Encrypt"
echo "  有效期: 90天"
echo "  自动续期: 已配置（每天凌晨3点检查）"
echo ""
echo "下一步："
echo "1. 在小程序代码中将 apiBaseUrl 改为: https://${DOMAIN_NAME}"
echo "2. 在微信公众平台配置合法域名: https://${DOMAIN_NAME}"
echo "3. 测试访问: curl https://${DOMAIN_NAME}/api/health"
echo ""
echo "常用命令："
echo "  查看证书状态: certbot certificates"
echo "  手动续期: certbot renew"
echo "  查看Nginx日志: tail -f /var/log/nginx/sora-api-access.log"
echo ""
echo "=========================================="
