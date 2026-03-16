#!/bin/bash

# 快速更新脚本 - 上传并重启服务

SERVER="root@8.211.175.227"
REMOTE_DIR="/home/admin/SoraMiniProgram/api_server"

echo "========================================="
echo "  快速更新到服务器"
echo "========================================="
echo "服务器: $SERVER"
echo "远程目录: $REMOTE_DIR"
echo ""

# 上传Python文件
echo "[1/3] 上传 sora_api.py..."
scp sora_api.py ${SERVER}:${REMOTE_DIR}/
if [ $? -ne 0 ]; then
    echo "❌ 上传失败"
    exit 1
fi
echo "✅ 上传完成"

# 上传配置
echo "[2/3] 上传 nginx-https.conf 和 setup_nginx_https.sh..."
scp nginx-https.conf setup_nginx_https.sh ${SERVER}:${REMOTE_DIR}/
if [ $? -ne 0 ]; then
    echo "❌ 上传失败"
    exit 1
fi
echo "✅ 上传完成"

# 执行更新脚本
echo "[3/3] 执行更新..."
ssh ${SERVER} "cd ${REMOTE_DIR} && bash setup_nginx_https.sh"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ 更新完成！"
    echo "========================================="
else
    echo ""
    echo "❌ 更新失败"
    exit 1
fi
