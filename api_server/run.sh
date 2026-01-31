#!/bin/bash

echo "Starting Sora API Server..."
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null
then
    echo "Error: Python3 is not installed"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 启动服务器
echo ""
echo "Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop"
python sora_api.py
