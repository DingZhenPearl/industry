@echo off
chcp 936 > nul
echo 正在停止Docker容器...

cd docker\config

docker-compose down

echo ======================================================
echo 容器已停止！
echo ======================================================
echo 如需重新启动应用，请运行: docker-start.bat
echo.
cd ..\..
pause
