#!/bin/bash

cd /home/admin/SoraMiniProgram/api_server

echo "1. 停止 systemd 服务..."
sudo systemctl stop sora-api 2>/dev/null || echo "服务未运行或不存在"

echo "2. 禁用 systemd 自动启动..."
sudo systemctl disable sora-api 2>/dev/null || echo "服务未启用"

echo "3. 等待2秒..."
sleep 2

echo "4. 确认没有残留进程..."
ps aux | grep -v grep | grep gunicorn | awk '{print $2}' | xargs -r sudo kill -9 2>/dev/null
ps aux | grep -v grep | grep sora_api.py | awk '{print $2}' | xargs -r sudo kill -9 2>/dev/null

echo "5. 激活虚拟环境..."
source venv/bin/activate

echo "6. 安装 Pillow..."
pip install -q pillow

echo "7. 启动服务（使用 python 直接启动）..."
nohup python sora_api.py > server.log 2>&1 &

echo "8. 等待5秒..."
sleep 5

echo "9. 检查状态..."
ps aux | grep -v grep | grep sora_api.py
sudo lsof -i :5000

echo ""
echo "Done! 服务已使用 python 直接启动，不再依赖 systemd"
