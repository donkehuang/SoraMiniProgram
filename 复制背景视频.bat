@echo off
echo ========================================
echo 复制背景视频到 API 服务器
echo ========================================
echo.

echo [1/2] 正在复制视频文件...
copy /Y "c:\Users\donke\Desktop\LuckyTalk\miniprogram\assets\background.mp4" "c:\Users\donke\Desktop\LuckyTalk\api_server\generated_videos\background.mp4"

if %errorlevel% == 0 (
    echo [√] 复制成功！
    echo.
    echo [2/2] 验证文件...
    dir "c:\Users\donke\Desktop\LuckyTalk\api_server\generated_videos\background.mp4"
    echo.
    echo ========================================
    echo √ 完成！现在可以编译小程序了
    echo ========================================
) else (
    echo [×] 复制失败！
    echo 请检查文件路径是否正确
)

echo.
pause
