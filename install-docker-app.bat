@echo off
chcp 936 > nul
echo 正在安装工厂智能管理系统...

REM 检查Docker是否安装
docker --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Docker，请先安装Docker
    echo 您可以从 https://www.docker.com/products/docker-desktop 下载Docker Desktop
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Docker Compose，请先安装Docker Compose
    echo Docker Desktop通常已包含Docker Compose
    exit /b 1
)

echo ======================================================
echo 步骤1: 准备环境
echo ======================================================

REM 检查是否有预先导出的镜像
if exist "industry-app.tar" (
    echo 发现预先导出的应用镜像，正在加载...
    docker load -i industry-app.tar
    echo 应用镜像加载完成
)

if exist "mysql-8.0.tar" (
    echo 发现预先导出的MySQL镜像，正在加载...
    docker load -i mysql-8.0.tar
    echo MySQL镜像加载完成
)

echo ======================================================
echo 步骤2: 启动数据库容器
echo ======================================================
echo 正在启动MySQL容器...
docker-compose up -d mysql

echo 等待MySQL容器启动和初始化 (这可能需要一分钟)...
timeout /t 60 /nobreak > nul

echo ======================================================
echo 步骤3: 导入数据库
echo ======================================================

REM 检查是否有数据库转储文件
if exist "full_db_dump.sql" (
    echo 发现数据库转储文件，正在导入...

    REM 将转储文件复制到容器
    docker cp full_db_dump.sql industry-mysql:/tmp/

    REM 在容器中执行导入
    docker exec -i industry-mysql mysql -uroot -pmwYgR7#*X2 < full_db_dump.sql

    if %ERRORLEVEL% NEQ 0 (
        echo 警告: 数据库导入可能未完全成功，但将继续安装
    ) else (
        echo 数据库导入成功
    )
) else (
    echo 未找到数据库转储文件，将使用默认初始化
)

echo ======================================================
echo 步骤4: 启动应用容器
echo ======================================================
echo 正在启动应用容器...
docker-compose up -d app

echo ======================================================
echo 安装完成！
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
echo 感谢使用工厂智能管理系统！
pause
