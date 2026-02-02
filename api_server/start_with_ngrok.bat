@echo off
chcp 65001 >nul
echo ========================================
echo     Sora API Server + ngrok 启动脚本
echo ========================================
echo.

REM 检查 ngrok 是否存在
if exist "C:\ngrok\ngrok.exe" (
    echo [✓] 找到 ngrok
) else (
    echo [X] 未找到 ngrok，请先下载：
    echo     https://ngrok.com/download
    echo     解压到 C:\ngrok\ 目录
    echo.
    pause
    exit
)

echo [1/2] 启动 API Server...
start "Sora API Server" cmd /k "cd /d %~dp0 && python sora_api.py"

echo [2/2] 等待服务器启动...
timeout /t 5 /nobreak >nul

echo [3/3] 启动 ngrok 内网穿透...
start "ngrok" cmd /k "C:\ngrok\ngrok.exe http 5000"

echo.
echo ========================================
echo           启动完成！
echo ========================================
echo.
echo 请查看 ngrok 窗口中的 Forwarding 地址
echo 格式：https://xxxx.ngrok-free.app
echo.
echo 将这个地址配置到小程序的 API_BASE 中即可
echo ========================================
pause
