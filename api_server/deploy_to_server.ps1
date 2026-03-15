# ===================================================================
# API服务器一键部署脚本 (PowerShell)
# 服务器: 8.211.175.227
# ===================================================================

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Green
Write-Host "  LuckyTalk API服务器部署" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

$SERVER = "root@8.211.175.227"
$SERVER_DIR = "/root/luckytalk-api"
$LOCAL_DIR = Get-Location

Write-Host "服务器: $SERVER" -ForegroundColor Cyan
Write-Host "本地目录: $LOCAL_DIR" -ForegroundColor Cyan
Write-Host "服务器目录: $SERVER_DIR" -ForegroundColor Cyan
Write-Host ""

# 检查是否安装了 SSH 客户端
$sshInstalled = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshInstalled) {
    Write-Host "错误: 未找到 SSH 客户端" -ForegroundColor Red
    Write-Host "请安装 OpenSSH 客户端或使用 Git Bash" -ForegroundColor Yellow
    exit 1
}

# 步骤1: 创建服务器目录并上传代码
Write-Host "[1/6] 上传代码到服务器..." -ForegroundColor Yellow
ssh $SERVER "mkdir -p $SERVER_DIR"

# 使用 scp 上传必要文件
Write-Host "正在上传文件..." -ForegroundColor Cyan
scp -r .\sora_api.py "$SERVER`:$SERVER_DIR/"
scp -r .\requirements.txt "$SERVER`:$SERVER_DIR/"
scp -r .\deploy.sh "$SERVER`:$SERVER_DIR/"
scp -r .\deploy_systemd.sh "$SERVER`:$SERVER_DIR/"
scp -r .\sora-api.service "$SERVER`:$SERVER_DIR/"
scp -r .\setup_https.sh "$SERVER`:$SERVER_DIR/"
scp -r .\.env.example "$SERVER`:$SERVER_DIR/"
scp -r .\nginx.conf "$SERVER`:$SERVER_DIR/"

Write-Host "✓ 代码上传完成" -ForegroundColor Green
Write-Host ""

# 步骤2: 配置环境变量
Write-Host "[2/6] 配置环境变量..." -ForegroundColor Yellow
ssh $SERVER "cd $SERVER_DIR && if [ ! -f .env ]; then cp .env.example .env; fi"

# 询问API Key
Write-Host ""
Write-Host "请输入你的 OpenAI API Key:" -ForegroundColor Cyan
$API_KEY = Read-Host -AsSecureString
$API_KEY_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($API_KEY))

ssh $SERVER "cd $SERVER_DIR && sed -i 's/your_openai_api_key_here/$API_KEY_PLAIN/' .env"
Write-Host "✓ 环境变量配置完成" -ForegroundColor Green
Write-Host ""

# 步骤3: 在服务器上执行部署脚本
Write-Host "[3/6] 在服务器上安装依赖..." -ForegroundColor Yellow
ssh $SERVER "cd $SERVER_DIR && bash deploy.sh"
Write-Host ""

# 步骤4: 启动服务
Write-Host "[4/6] 启动 API 服务..." -ForegroundColor Yellow
ssh $SERVER "cd $SERVER_DIR && source venv/bin/activate && nohup python sora_api.py > server.log 2>&1 &"
Start-Sleep -Seconds 3

# 检查服务是否启动
Write-Host "[5/6] 检查服务状态..." -ForegroundColor Yellow
ssh $SERVER "ps aux | grep sora_api.py | grep -v grep"

# 测试API
Write-Host ""
Write-Host "[6/6] 测试API接口..." -ForegroundColor Yellow
ssh $SERVER "curl -s http://localhost:5000/api/health"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "服务器信息:" -ForegroundColor Cyan
Write-Host "  - IP: 8.211.175.227" -ForegroundColor White
Write-Host "  - HTTP API: http://8.211.175.227:5000" -ForegroundColor White
Write-Host "  - 健康检查: http://8.211.175.227:5000/api/health" -ForegroundColor White
Write-Host ""
Write-Host "查看日志:" -ForegroundColor Cyan
Write-Host "  ssh $SERVER 'cd $SERVER_DIR && tail -f server.log'" -ForegroundColor White
Write-Host ""
Write-Host "下一步配置 HTTPS:" -ForegroundColor Cyan
Write-Host "  1. 购买域名并解析到 8.211.175.227" -ForegroundColor White
Write-Host "  2. 申请SSL证书" -ForegroundColor White
Write-Host "  3. 运行: ssh $SERVER 'cd $SERVER_DIR && bash setup_https.sh'" -ForegroundColor White
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
