#!/bin/bash

# 使用 systemd 配置开机自启动

echo "========================================="
echo "  配置 Sora API Server 开机自启动"
echo "========================================="

# 获取当前目录的绝对路径
CURRENT_DIR=$(pwd)
SERVICE_FILE="sora-api.service"
SYSTEMD_PATH="/etc/systemd/system/sora-api.service"

# 检查是否有 root 权限
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  请使用 sudo 运行此脚本"
    echo "   命令: sudo bash deploy_systemd.sh"
    exit 1
fi

# 1. 替换 service 文件中的路径
echo "[1/5] 更新 service 文件中的路径..."
sed "s|/path/to/your/api_server|$CURRENT_DIR|g" $SERVICE_FILE > /tmp/sora-api.service

# 2. 复制 service 文件到 systemd 目录
echo "[2/5] 复制 service 文件..."
cp /tmp/sora-api.service $SYSTEMD_PATH

# 3. 重新加载 systemd
echo "[3/5] 重新加载 systemd..."
systemctl daemon-reload

# 4. 启用开机自启动
echo "[4/5] 启用开机自启动..."
systemctl enable sora-api

# 5. 启动服务
echo "[5/5] 启动服务..."
systemctl start sora-api

echo ""
echo "========================================="
echo "          配置完成！"
echo "========================================="
echo ""
echo "常用命令："
echo "  查看服务状态:   sudo systemctl status sora-api"
echo "  启动服务:       sudo systemctl start sora-api"
echo "  停止服务:       sudo systemctl stop sora-api"
echo "  重启服务:       sudo systemctl restart sora-api"
echo "  查看日志:       sudo journalctl -u sora-api -f"
echo "  禁用自启动:     sudo systemctl disable sora-api"
echo ""
echo "========================================="

# 显示服务状态
systemctl status sora-api
