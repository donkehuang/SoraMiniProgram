#!/bin/bash

echo "=========================================="
echo "强制终止 gunicorn 并重启"
echo "=========================================="

# 进入工作目录
cd /home/admin/SoraMiniProgram/api_server || exit 1

# 直接 kill 掉所有 gunicorn 进程
echo ""
echo "🛑 强制终止 gunicorn 进程..."
ps aux | grep -v grep | grep gunicorn | awk '{print $2}' | xargs -r kill -9

# 等待
sleep 3

# 再次检查
echo ""
echo "🔍 检查残留进程..."
if ps aux | grep -v grep | grep gunicorn > /dev/null; then
    echo "❌ 仍有残留进程:"
    ps aux | grep -v grep | grep gunicorn
    echo ""
    echo "再次尝试终止..."
    ps aux | grep -v grep | grep gunicorn | awk '{print $2}' | xargs -r sudo kill -9
    sleep 2
fi

# 检查端口
echo ""
echo "🔍 检查 5000 端口..."
if sudo lsof -i :5000 &>/dev/null; then
    echo "❌ 端口仍被占用:"
    sudo lsof -i :5000
    echo ""
    echo "强制终止占用端口的进程..."
    sudo lsof -t -i :5000 | xargs -r sudo kill -9
    sleep 3
fi

# 最终检查
echo ""
echo "🔍 最终检查..."
if sudo lsof -i :5000 &>/dev/null; then
    echo "❌ 端口仍被占用，无法启动"
    exit 1
else
    echo "✅ 端口已释放"
fi

# 激活虚拟环境
echo ""
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装依赖..."
pip install -q pillow

# 启动服务
echo ""
echo "🚀 启动服务..."
nohup python sora_api.py > server.log 2>&1 &

# 等待启动
sleep 5

# 检查状态
echo ""
echo "📊 检查服务状态..."
if ps aux | grep -v grep | grep sora_api.py > /dev/null; then
    echo "✅ 服务运行正常"
else
    echo "❌ 服务启动失败"
    tail -n 20 server.log
    exit 1
fi

if sudo lsof -i :5000 &>/dev/null; then
    echo "✅ 5000 端口监听中"
    sudo lsof -i :5000
else
    echo "❌ 5000 端口未监听"
fi

echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
