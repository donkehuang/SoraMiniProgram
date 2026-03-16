#!/bin/bash

# 更新并重启服务器

echo "=========================================="
echo "更新服务器"
echo "=========================================="

DOMAIN="www.enfuri51.xyz"
SERVER="root@8.211.175.227"

echo ""
echo "步骤 1: 上传最新代码..."
scp sora_api.py ${SERVER}:/root/luckytalk-api/
scp nginx-https.conf ${SERVER}:/root/luckytalk-api/

if [ $? -ne 0 ]; then
    echo "❌ 上传失败"
    exit 1
fi

echo "✅ 上传完成"
echo ""
echo "步骤 2: 更新Nginx配置..."
ssh ${SERVER} << 'EOF'
cd /root/luckytalk-api
sudo cp nginx-https.conf /etc/nginx/sites-available/sora-api
sudo ln -sf /etc/nginx/sites-available/sora-api /etc/nginx/sites-enabled/sora-api
sudo nginx -t
EOF

if [ $? -ne 0 ]; then
    echo "❌ Nginx配置测试失败"
    exit 1
fi

echo "✅ Nginx配置更新完成"
echo ""
echo "步骤 3: 重启服务..."
ssh ${SERVER} << 'EOF'
cd /root/luckytalk-api

# 重启Flask服务
pkill -f sora_api.py
source venv/bin/activate
nohup python sora_api.py > server.log 2>&1 &

# 重启Nginx
sudo systemctl restart nginx

# 等待服务启动
sleep 3

# 检查服务状态
echo "检查Flask服务:"
ps aux | grep sora_api.py | grep -v grep

echo ""
echo "检查Nginx服务:"
sudo systemctl status nginx --no-pager
EOF

if [ $? -ne 0 ]; then
    echo "❌ 服务重启失败"
    exit 1
fi

echo ""
echo "✅ 服务重启完成"
echo ""
echo "步骤 4: 测试API..."
curl -s https://${DOMAIN}/api/health

echo ""
echo ""
echo "=========================================="
echo "✅ 更新完成！"
echo "=========================================="
echo "API地址: https://${DOMAIN}"
echo "查看日志: ssh ${SERVER} 'tail -f /root/luckytalk-api/server.log'"
echo "=========================================="
