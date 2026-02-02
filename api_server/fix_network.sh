#!/bin/bash

echo "=========================================="
echo "API服务器网络修复工具"
echo "=========================================="
echo ""

# 1. 开放防火墙端口
echo "1️⃣ 开放防火墙5000端口..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 5000
    echo "✅ UFW防火墙已开放5000端口"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload
    echo "✅ firewalld已开放5000端口"
else
    echo "⚠️  未检测到防火墙管理工具"
fi
echo ""

# 2. 确保服务监听0.0.0.0
echo "2️⃣ 检查服务配置..."
SERVICE_FILE="/etc/systemd/system/sora-api.service"

if grep -q "0.0.0.0:5000" "$SERVICE_FILE"; then
    echo "✅ 服务已配置监听0.0.0.0:5000"
else
    echo "⚠️  需要修改服务配置"
    echo "当前配置:"
    grep "ExecStart" "$SERVICE_FILE"
    echo ""
    echo "请手动修改 $SERVICE_FILE"
    echo "确保 ExecStart 中包含: -b 0.0.0.0:5000"
fi
echo ""

# 3. 重启服务
echo "3️⃣ 重启API服务..."
sudo systemctl daemon-reload
sudo systemctl restart sora-api
sleep 2
echo ""

# 4. 验证服务状态
echo "4️⃣ 验证服务状态..."
if sudo systemctl is-active --quiet sora-api; then
    echo "✅ 服务运行中"
    
    # 测试本地访问
    if curl -s http://localhost:5000/api/health > /dev/null; then
        echo "✅ 本地访问成功"
    else
        echo "❌ 本地访问失败"
    fi
else
    echo "❌ 服务未运行"
    sudo systemctl status sora-api --no-pager
fi
echo ""

# 5. 显示监听端口
echo "5️⃣ 当前监听端口:"
sudo netstat -tlnp | grep 5000
echo ""

echo "=========================================="
echo "⚠️  最重要：配置阿里云安全组"
echo "=========================================="
echo "服务器端配置完成后，必须在阿里云控制台配置安全组："
echo ""
echo "步骤："
echo "1. 登录阿里云控制台 (https://ecs.console.aliyun.com)"
echo "2. 找到你的ECS实例 (IP: 8.211.175.227)"
echo "3. 点击 '安全组配置'"
echo "4. 点击 '配置规则' → '添加安全组规则'"
echo "5. 入方向规则设置："
echo "   - 协议类型: 自定义TCP"
echo "   - 端口范围: 5000/5000"
echo "   - 授权对象: 0.0.0.0/0"
echo "   - 描述: Sora API服务"
echo "6. 点击 '确定' 保存"
echo ""
echo "配置完成后，从本地测试："
echo "curl http://8.211.175.227:5000/api/health"
echo "=========================================="
