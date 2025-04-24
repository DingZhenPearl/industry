@echo off
chcp 936 > nul
echo 正在准备数据库以便共享...

REM 设置参数
set MYSQL_CONTAINER=industry-mysql
set EXPORT_FILE=industry_db_dump.sql

echo ======================================================
echo 步骤1: 检查Docker容器是否运行
echo ======================================================
docker ps | findstr %MYSQL_CONTAINER% > nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: MySQL容器未运行
    echo 请先启动容器: docker-compose up -d mysql
    exit /b 1
)

echo ======================================================
echo 步骤2: 导出数据库
echo ======================================================
echo 正在从Docker容器导出数据库...

REM 导出完整数据库，包括创建数据库语句和所有表结构及数据
docker exec -i %MYSQL_CONTAINER% mysqldump -uroot -pmwYgR7#*X2 --databases industry_db --add-drop-database --routines --events --triggers > %EXPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo 错误: 数据库导出失败
    exit /b 1
)

echo 数据库导出成功！文件: %EXPORT_FILE%

echo ======================================================
echo 步骤3: 准备共享文件
echo ======================================================

REM 创建共享目录
if not exist "share" mkdir share

REM 复制必要文件到共享目录
copy %EXPORT_FILE% share\
copy docker-compose.yml share\
copy Dockerfile share\
copy README.md share\ 2>nul
copy install-docker-app.bat share\

echo ======================================================
echo 步骤4: 导出Docker镜像
echo ======================================================
echo 是否要导出Docker镜像? 这将创建较大的文件，但接收方不需要构建镜像 (Y/N)
set /p EXPORT_IMAGES=

if /i "%EXPORT_IMAGES%"=="Y" (
    echo 正在导出应用镜像...
    docker save -o share\industry-app.tar industry-app
    
    echo 正在导出MySQL镜像...
    docker save -o share\mysql-8.0.tar mysql:8.0
    
    echo 镜像导出完成！
) else (
    echo 跳过镜像导出，接收方将需要自行构建镜像
)

echo ======================================================
echo 准备完成！
echo ======================================================
echo 共享文件已准备好，位于 "share" 目录
echo 请将此目录的内容分享给其他人
