#!/bin/bash

echo "=========================================="
echo "清理 5000 端口并重启服务"
echo "=========================================="

# 查找占用 5000 端口的进程
echo "🔍 检查 5000 端口占用情况..."
if sudo lsof -i :5000 &>/dev/null; then
    echo "占用 5000 端口的进程:"
    sudo lsof -i :5000
else
    echo "✅ 5000 端口未被占用"
fi

# 停止所有 sora_api.py 相关进程
echo ""
echo "🛑 停止 sora_api.py 进程..."
pkill -9 -f sora_api.py 2>/dev/null || echo "没有找到 sora_api.py 进程"

# 停止所有占用 5000 端口的进程
echo ""
echo "🛑 强制终止占用 5000 端口的进程..."
if sudo lsof -t -i :5000 &>/dev/null; then
    sudo lsof -t -i :5000 | xargs -r sudo kill -9
    echo "✅ 已终止"
else
    echo "没有进程占用 5000 端口"
fi

# 等待端口释放
echo ""
echo "⏱️  等待端口释放..."
sleep 3

# 再次检查
echo ""
echo "🔍 最终检查..."
if sudo lsof -i :5000 &>/dev/null; then
    echo "❌ 警告：5000 端口仍被占用"
    sudo lsof -i :5000
    echo ""
    echo "请手动清理后运行:"
    echo "  sudo kill -9 <PID>"
    exit 1
else
    echo "✅ 5000 端口已释放"
fi

# 进入工作目录
cd /home/admin/SoraMiniProgram/api_server || exit 1

# 激活虚拟环境
echo ""
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
pip install -q pillow

# 验证安装
python -c "from PIL import Image; print('✅ PIL/Pillow 验证成功')"

# 启动服务
echo ""
echo "🚀 启动 Flask 服务..."
nohup python sora_api.py > server.log 2>&1 &

# 等待服务启动
sleep 5

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
if ps aux | grep -v grep | grep sora_api.py > /dev/null; then
    echo "✅ Flask API 服务运行正常"

    # 显示日志
    echo ""
    echo "📋 最近 20 行日志:"
    tail -n 20 server.log

    echo ""
    echo "=========================================="
    echo "✅ 重启完成！"
    echo "=========================================="
    echo "API 地址: https://www.enfuri51.xyz/api/health"
    echo "查看日志: tail -f server.log"
    echo "=========================================="
else
    echo "❌ Flask API 服务启动失败"
    echo "查看日志:"
    tail -n 30 server.log
    exit 1
fi
