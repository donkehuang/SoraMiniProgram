#!/bin/bash

echo "=========================================="
echo "完整清理并重启服务"
echo "=========================================="

# 进入工作目录
cd /home/admin/SoraMiniProgram/api_server || exit 1

# 停止所有 gunicorn 进程
echo ""
echo "🛑 停止所有 gunicorn 进程..."
pkill -9 -f gunicorn 2>/dev/null || echo "没有找到 gunicorn 进程"
killall -9 gunicorn 2>/dev/null || true

# 停止所有 sora_api.py 进程
echo "🛑 停止所有 sora_api.py 进程..."
pkill -9 -f sora_api.py 2>/dev/null || echo "没有找到 sora_api.py 进程"

# 停止所有占用 5000 端口的进程
echo "🛑 停止所有占用 5000 端口的进程..."
if sudo lsof -t -i :5000 &>/dev/null; then
    sudo lsof -t -i :5000 | xargs -r sudo kill -9
    echo "✅ 已终止"
else
    echo "没有进程占用 5000 端口"
fi

# 直接 kill 掉所有 gunicorn PID（如果存在）
if ps aux | grep -v grep | grep gunicorn > /dev/null; then
    echo "🛑 发现残留 gunicorn 进程，强制终止..."
    ps aux | grep -v grep | grep gunicorn | awk '{print $2}' | xargs -r kill -9
    echo "✅ 已终止残留进程"
fi

# 等待端口释放
echo ""
echo "⏱️  等待端口释放..."
sleep 5

# 再次检查
echo ""
echo "🔍 最终检查..."
if sudo lsof -i :5000 &>/dev/null; then
    echo "❌ 警告：5000 端口仍被占用"
    sudo lsof -i :5000
    echo ""
    echo "请手动清理:"
    echo "  sudo kill -9 <PID>"
    exit 1
else
    echo "✅ 5000 端口已释放"
fi

# 激活虚拟环境
echo ""
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装/验证 Python 依赖..."
pip install -q pillow flask flask-cors openai python-dotenv

# 验证安装
python -c "from PIL import Image; print('✅ PIL/Pillow 验证成功')"

# 使用 gunicorn 启动服务（如果可用）
if command -v gunicorn &> /dev/null; then
    echo ""
    echo "🚀 使用 gunicorn 启动服务..."
    
    # 检查是否有 gunicorn 配置文件
    if [ -f "gunicorn_config.py" ]; then
        nohup gunicorn -c gunicorn_config.py sora_api:app > server.log 2>&1 &
    else
        nohup gunicorn -w 4 -b 0.0.0.0:5000 sora_api:app > server.log 2>&1 &
    fi
else
    echo ""
    echo "🚀 使用 python 直接启动服务..."
    nohup python sora_api.py > server.log 2>&1 &
fi

# 等待服务启动
sleep 5

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
if ps aux | grep -v grep | grep -E "(sora_api.py|gunicorn)" > /dev/null; then
    echo "✅ 服务进程运行正常"
    ps aux | grep -v grep | grep -E "(sora_api.py|gunicorn)"
else
    echo "❌ 服务进程未运行"
fi

# 检查端口
echo ""
echo "🔍 检查端口状态..."
if sudo lsof -i :5000 &>/dev/null; then
    echo "✅ 5000 端口正在监听"
    sudo lsof -i :5000
else
    echo "❌ 5000 端口未监听"
fi

# 显示日志
echo ""
echo "📋 最近 30 行日志:"
tail -n 30 server.log

# 测试 API
echo ""
echo "🧪 测试 API..."
sleep 2
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ 本地 API 测试成功"
else
    echo "❌ 本地 API 测试失败"
fi

echo ""
echo "=========================================="
echo "✅ 重启完成！"
echo "=========================================="
echo "API 地址: https://www.enfuri51.xyz/api/health"
echo "查看日志: tail -f server.log"
echo "=========================================="
