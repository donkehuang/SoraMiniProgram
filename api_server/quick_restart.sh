#!/bin/bash

cd /home/admin/SoraMiniProgram/api_server

echo "1. 停止进程..."
ps aux | grep -v grep | grep gunicorn | awk '{print $2}' | xargs -r kill -9 2>/dev/null
ps aux | grep -v grep | grep sora_api.py | awk '{print $2}' | xargs -r kill -9 2>/dev/null

echo "2. 等待2秒..."
sleep 2

echo "3. 激活虚拟环境..."
source venv/bin/activate

echo "4. 启动服务..."
nohup python sora_api.py > server.log 2>&1 &

echo "5. 等待5秒..."
sleep 5

echo "6. 检查状态..."
ps aux | grep -v grep | grep sora_api.py
sudo lsof -i :5000

echo "Done!"
