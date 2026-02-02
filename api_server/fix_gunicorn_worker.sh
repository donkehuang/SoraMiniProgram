#!/bin/bash

echo "=========================================="
echo "修复Gunicorn多Worker问题"
echo "=========================================="
echo ""

echo "问题：Gunicorn使用4个worker，导致内存中的video_tasks不共享"
echo "解决：改为1个worker（对于Sora API这种高延迟任务更合适）"
echo ""

# 修改systemd服务文件
sudo tee /etc/systemd/system/sora-api.service > /dev/null << 'EOF'
[Unit]
Description=Sora API Service
After=network.target

[Service]
Type=simple
User=admin
Group=admin
WorkingDirectory=/home/admin/SoraMiniProgram/api_server
Environment="PATH=/home/admin/SoraMiniProgram/api_server/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/admin/SoraMiniProgram/api_server/venv/bin/gunicorn -w 1 -b 0.0.0.0:5000 --timeout 600 --worker-class sync sora_api:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "✅ 服务文件已更新（worker数量：1）"
echo ""

# 重新加载并重启
echo "重新加载systemd配置..."
sudo systemctl daemon-reload

echo "重启服务..."
sudo systemctl restart sora-api

sleep 2

echo "检查服务状态..."
sudo systemctl status sora-api --no-pager -l

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "说明："
echo "- 单worker模式更适合Sora这种高延迟API"
echo "- 内存状态不会在多进程间丢失"
echo "- 性能足够处理小程序的并发请求"
echo ""
