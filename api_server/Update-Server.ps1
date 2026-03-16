# 更新服务器代码并配置 Nginx HTTPS

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "更新服务器代码并配置 Nginx HTTPS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$LocalDir = "C:\Users\donke\Desktop\LuckyTalk\api_server"
$Server = "root@8.211.175.227"
$RemoteDir = "/root/luckytalk-api"

# 检查是否在正确的目录
if (-not (Test-Path "$LocalDir\sora_api.py")) {
    Write-Host "❌ 错误: 请先切换到 api_server 目录" -ForegroundColor Red
    exit 1
}

# 步骤 1: 上传文件
Write-Host "`n步骤 1: 上传代码到服务器..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Gray

Set-Location $LocalDir

Write-Host "上传 sora_api.py..." -ForegroundColor White
$result = scp sora_api.py "${Server}:${RemoteDir}/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 上传 sora_api.py 失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host "✅ sora_api.py 上传完成" -ForegroundColor Green

Write-Host "上传 nginx-https.conf..." -ForegroundColor White
$result = scp nginx-https.conf "${Server}:${RemoteDir}/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 上传 nginx-https.conf 失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host "✅ nginx-https.conf 上传完成" -ForegroundColor Green

Write-Host "上传 setup_nginx_https.sh..." -ForegroundColor White
$result = scp setup_nginx_https.sh "${Server}:${RemoteDir}/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 上传 setup_nginx_https.sh 失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host "✅ setup_nginx_https.sh 上传完成" -ForegroundColor Green

# 步骤 2: 在服务器上执行更新脚本
Write-Host "`n步骤 2: 在服务器上执行更新..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Gray

Write-Host "执行 setup_nginx_https.sh..." -ForegroundColor White
ssh $Server "cd $RemoteDir && bash setup_nginx_https.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "✅ 更新完成！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "API 地址: https://www.enfuri51.xyz" -ForegroundColor White
    Write-Host "查看日志: ssh $Server 'tail -f /root/luckytalk-api/server.log'" -ForegroundColor Gray
    Write-Host "==========================================" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ 更新失败，请检查错误信息" -ForegroundColor Red
}

Read-Host "`n按回车键退出"
