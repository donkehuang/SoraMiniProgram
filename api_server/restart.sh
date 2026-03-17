#!/bin/bash

echo "=========================================="
echo "重启 Flask API 服务"
echo "=========================================="

WORK_DIR="/home/admin/SoraMiniProgram/api_server"

cd "$WORK_DIR" || exit 1

# 1. 停止所有 sora_api.py 进程
echo "🛑 停止现有服务..."
pkill -9 -f sora_api.py 2>/dev/null || echo "没有找到进程"

# 2. 停止占用 5000 端口的进程
if sudo lsof -i :5000 &>/dev/null; then
    echo "🛑 清理 5000 端口..."
    sudo lsof -t -i :5000 | xargs -r kill -9 2>/dev/null
fi

sleep 3

# 3. 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 4. 安装依赖
echo "📦 安装依赖..."
pip install -q pillow

# 5. 启动服务
echo "🚀 启动服务..."
nohup python sora_api.py > server.log 2>&1 &

sleep 5

# 6. 检查状态
echo "📊 检查服务状态..."
ps aux | grep sora_api.py | grep -v grep

echo ""
echo "=========================================="
echo "✅ 重启完成！"
echo "=========================================="
echo "查看日志: tail -f $WORK_DIR/server.log"
echo "=========================================="
