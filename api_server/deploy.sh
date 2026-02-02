#!/bin/bash

# Sora API Server 部署脚本（Linux/Ubuntu）

echo "========================================="
echo "  Sora API Server 自动部署脚本"
echo "========================================="

# 1. 更新系统
echo "[1/8] 更新系统包..."
sudo apt-get update

# 2. 安装 Python 和 pip
echo "[2/8] 安装 Python3 和 pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# 3. 创建虚拟环境
echo "[3/8] 创建 Python 虚拟环境..."
python3 -m venv venv

# 4. 激活虚拟环境
echo "[4/8] 激活虚拟环境..."
source venv/bin/activate

# 5. 升级 pip
echo "[5/8] 升级 pip..."
pip install --upgrade pip

# 6. 安装依赖
echo "[6/8] 安装 Python 依赖..."
pip install -r requirements.txt

# 7. 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    echo "[7/8] 创建 .env 配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入你的 OPENAI_API_KEY"
    echo "   命令: nano .env"
else
    echo "[7/8] .env 文件已存在，跳过..."
fi

# 8. 创建视频存储目录
echo "[8/8] 创建视频存储目录..."
mkdir -p generated_videos

echo ""
echo "========================================="
echo "          部署完成！"
echo "========================================="
echo ""
echo "接下来的步骤："
echo "1. 编辑 .env 文件，设置 OPENAI_API_KEY"
echo "   命令: nano .env"
echo ""
echo "2. 启动服务（开发模式）："
echo "   source venv/bin/activate"
echo "   python sora_api.py"
echo ""
echo "3. 启动服务（生产模式，使用 Gunicorn）："
echo "   source venv/bin/activate"
echo "   gunicorn -w 4 -b 0.0.0.0:5000 sora_api:app"
echo ""
echo "4. 后台运行（使用 systemd 或 supervisor）"
echo "   参考 deploy_systemd.sh 脚本"
echo ""
echo "========================================="
