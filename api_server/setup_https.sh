#!/bin/bash
# HTTPS配置脚本 - 为API服务器配置HTTPS访问

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

# 1. 安装Nginx
echo "[步骤1] 安装Nginx..."
if ! command -v nginx &> /dev/null; then
    apt update
    apt install -y nginx
    echo "✓ Nginx安装完成"
else
    echo "✓ Nginx已安装"
fi

# 2. 创建证书目录
echo ""
echo "[步骤2] 创建SSL证书目录..."
mkdir -p /etc/nginx/ssl
echo "✓ 证书目录创建完成: /etc/nginx/ssl"
echo ""
echo "请将SSL证书文件上传到此目录："
echo "  - 证书文件: /etc/nginx/ssl/api.yourapp.com.pem"
echo "  - 私钥文件: /etc/nginx/ssl/api.yourapp.com.key"
echo ""
read -p "证书已上传？按Enter继续，或按Ctrl+C取消..."

# 3. 创建Nginx配置
echo ""
echo "[步骤3] 创建Nginx配置..."

# 提示输入域名
read -p "请输入你的API域名（例如: api.luckyapp.com）: " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    echo "错误: 域名不能为空"
    exit 1
fi

# 创建Nginx配置文件
cat > /etc/nginx/sites-available/sora-api << EOF
# API服务器HTTPS配置
server {
    listen 80;
    server_name ${DOMAIN_NAME};
    
    # HTTP自动跳转到HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN_NAME};
    
    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/${DOMAIN_NAME}.pem;
    ssl_certificate_key /etc/nginx/ssl/${DOMAIN_NAME}.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
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
        alias /root/SoraMiniProgram/api_server/generated_videos/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

echo "✓ Nginx配置文件创建完成"

# 4. 启用配置
echo ""
echo "[步骤4] 启用Nginx配置..."
ln -sf /etc/nginx/sites-available/sora-api /etc/nginx/sites-enabled/
echo "✓ 配置已启用"

# 5. 测试配置
echo ""
echo "[步骤5] 测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx配置测试通过"
else
    echo "✗ Nginx配置测试失败，请检查配置"
    exit 1
fi

# 6. 重启Nginx
echo ""
echo "[步骤6] 重启Nginx..."
systemctl restart nginx
systemctl enable nginx
echo "✓ Nginx已重启并设置为开机自启"

# 7. 配置防火墙
echo ""
echo "[步骤7] 配置防火墙..."
echo "请确保阿里云安全组已开放以下端口："
echo "  - 80 (HTTP)"
echo "  - 443 (HTTPS)"
echo ""

# 8. 完成
echo ""
echo "=========================================="
echo "✓ HTTPS配置完成！"
echo "=========================================="
echo ""
echo "你的API地址现在是: https://${DOMAIN_NAME}"
echo ""
echo "下一步："
echo "1. 在小程序代码中将 apiBaseUrl 改为: https://${DOMAIN_NAME}"
echo "2. 在微信公众平台配置合法域名: https://${DOMAIN_NAME}"
echo "3. 测试访问: curl https://${DOMAIN_NAME}/api/health"
echo ""
