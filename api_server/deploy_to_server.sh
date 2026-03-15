#!/bin/bash

# ===================================================================
# API服务器一键部署脚本
# 服务器: 8.211.175.227
# ===================================================================

SERVER="root@8.211.175.227"
SERVER_DIR="/root/luckytalk-api"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "  LuckyTalk API服务器部署"
echo "========================================="
echo "服务器: $SERVER"
echo "本地目录: $LOCAL_DIR"
echo "服务器目录: $SERVER_DIR"
echo ""

# 步骤1: 创建服务器目录并上传代码
echo "[1/6] 上传代码到服务器..."
ssh $SERVER "mkdir -p $SERVER_DIR"

# 排除不必要的文件
rsync -avz --progress \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='.git' \
    --exclude='generated_videos/*' \
    --exclude='*.bat' \
    $LOCAL_DIR/ $SERVER:$SERVER_DIR/

echo "✓ 代码上传完成"
echo ""

# 步骤2: 配置环境变量
echo "[2/6] 配置环境变量..."
ssh $SERVER "cd $SERVER_DIR && if [ ! -f .env ]; then cp .env.example .env; fi"

# 询问API Key
echo ""
echo "请输入你的 OpenAI API Key:"
read -s API_KEY
echo ""

ssh $SERVER "cd $SERVER_DIR && sed -i 's/your_openai_api_key_here/$API_KEY/' .env"
echo "✓ 环境变量配置完成"
echo ""

# 步骤3: 在服务器上执行部署脚本
echo "[3/6] 在服务器上安装依赖..."
ssh $SERVER "cd $SERVER_DIR && bash deploy.sh"
echo ""

# 步骤4: 启动服务
echo "[4/6] 启动 API 服务..."
ssh $SERVER "cd $SERVER_DIR && source venv/bin/activate && nohup python sora_api.py > server.log 2>&1 &"
sleep 3

# 检查服务是否启动
echo "[5/6] 检查服务状态..."
ssh $SERVER "ps aux | grep sora_api.py | grep -v grep"

# 测试API
echo ""
echo "[6/6] 测试API接口..."
ssh $SERVER "curl -s http://localhost:5000/api/health || echo 'API测试失败'"

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "服务器信息:"
echo "  - IP: 8.211.175.227"
echo "  - HTTP API: http://8.211.175.227:5000"
echo "  - 健康检查: http://8.211.175.227:5000/api/health"
echo ""
echo "查看日志:"
echo "  ssh $SERVER 'cd $SERVER_DIR && tail -f server.log'"
echo ""
echo "下一步配置 HTTPS:"
echo "  ssh $SERVER 'cd $SERVER_DIR && bash setup_https.sh'"
echo ""
echo "========================================="
