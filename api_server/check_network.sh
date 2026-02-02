#!/bin/bash

echo "=========================================="
echo "API服务器网络诊断工具"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "1️⃣ 检查API服务状态..."
sudo systemctl status sora-api --no-pager | grep -E "(Active|Main PID|loaded)"
echo ""

# 2. 检查端口监听
echo "2️⃣ 检查端口5000监听状态..."
sudo netstat -tlnp | grep 5000
echo ""

# 3. 检查服务绑定地址
echo "3️⃣ 检查服务绑定地址..."
ps aux | grep gunicorn | grep -v grep
echo ""

# 4. 测试本地访问
echo "4️⃣ 测试本地访问..."
curl -s http://localhost:5000/api/health || echo "❌ 本地访问失败"
curl -s http://127.0.0.1:5000/api/health || echo "❌ 127.0.0.1访问失败"
echo ""

# 5. 检查防火墙状态
echo "5️⃣ 检查防火墙状态..."
if command -v ufw &> /dev/null; then
    sudo ufw status | grep 5000
    echo "如果5000端口未开放，运行: sudo ufw allow 5000"
else
    echo "ufw未安装"
fi
echo ""

# 6. 检查SELinux（CentOS/RHEL）
echo "6️⃣ 检查SELinux状态..."
if command -v getenforce &> /dev/null; then
    getenforce
else
    echo "不适用（可能是Ubuntu）"
fi
echo ""

echo "=========================================="
echo "⚠️  重要提示："
echo "=========================================="
echo "1. 阿里云安全组必须开放5000端口"
echo "   - 登录阿里云控制台"
echo "   - 进入 ECS实例 → 安全组 → 配置规则"
echo "   - 添加入方向规则："
echo "     协议类型: TCP"
echo "     端口范围: 5000/5000"
echo "     授权对象: 0.0.0.0/0"
echo ""
echo "2. 如果服务监听127.0.0.1，需要修改为0.0.0.0"
echo "   运行: sudo nano /etc/systemd/system/sora-api.service"
echo "   确保ExecStart中有 -b 0.0.0.0:5000"
echo ""
echo "3. 修改后重启服务："
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl restart sora-api"
echo "=========================================="
