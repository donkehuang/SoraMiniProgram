@echo off
chcp 65001 > nul

echo ==========================================
echo 更新服务器代码和配置
echo ==========================================

set API_DIR=C:\Users\donke\Desktop\LuckyTalk\api_server
set SERVER=root@8.211.175.227
set REMOTE_DIR=/home/admin/SoraMiniProgram/api_server

echo.
echo 步骤 1: 上传代码到服务器...
echo ==========================================

cd /d "%API_DIR%"

scp sora_api.py %SERVER%:%REMOTE_DIR%/
if errorlevel 1 (
    echo ❌ 上传 sora_api.py 失败
    pause
    exit /b 1
)
echo ✅ sora_api.py 上传完成

scp nginx-https.conf %SERVER%:%REMOTE_DIR%/
if errorlevel 1 (
    echo ❌ 上传 nginx-https.conf 失败
    pause
    exit /b 1
)
echo ✅ nginx-https.conf 上传完成

echo.
echo ==========================================
echo 步骤 2: 在服务器上执行更新脚本
echo ==========================================
echo.
echo 请在SSH连接到服务器后执行以下命令:
echo.
echo   cd %REMOTE_DIR%
echo   bash update_server.sh
echo.
echo ==========================================
echo.
echo 或者继续在PowerShell中执行SSH命令:
echo.

pause
