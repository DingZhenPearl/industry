@echo off
chcp 936 > nul
echo 正在启动Docker容器...

cd docker\config

echo ======================================================
echo 步骤1: 启动MySQL容器
echo ======================================================
docker-compose up -d mysql

echo 等待MySQL容器启动和初始化 (这可能需要一分钟)...
timeout /t 30 /nobreak > nul

echo ======================================================
echo 步骤2: 启动应用容器
echo ======================================================
docker-compose up -d app

echo ======================================================
echo 启动完成！
echo ======================================================
echo 您现在可以访问: http://localhost:3000
echo 测试账号:
echo - 厂长: SP0001 / admin1
echo - 工长: FM0002 / foreman123
echo - 产线工人: WK0008 / worker123
echo - 安全员: SF0009 / safety123
echo.
echo 如需查看应用日志，请运行: docker-compose logs -f app
echo 如需停止应用，请运行: docker-compose down
echo 如需重启应用，请运行: docker-compose restart
echo.
cd ..\..
pause
