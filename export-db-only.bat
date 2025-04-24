@echo off
chcp 936 > nul
echo 正在导出数据库...

REM 设置参数
set MYSQL_CONTAINER=industry-mysql
set EXPORT_FILE=full_db_dump.sql

echo ======================================================
echo 检查Docker容器是否运行
echo ======================================================
docker ps | findstr %MYSQL_CONTAINER% > nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: MySQL容器未运行
    echo 请先启动容器: docker-compose up -d mysql
    exit /b 1
)

echo ======================================================
echo 导出数据库
echo ======================================================
echo 正在从Docker容器导出数据库...

REM 导出完整数据库，包括创建数据库语句和所有表结构及数据
docker exec -i %MYSQL_CONTAINER% mysqldump -uroot -pmwYgR7#*X2 --databases industry_db --add-drop-database --routines --events --triggers > %EXPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo 错误: 数据库导出失败
    exit /b 1
)

echo ======================================================
echo 数据库导出成功！
echo ======================================================
echo 文件: %EXPORT_FILE%
echo 现在您可以使用 create-sharing-package.bat 创建完整的共享包
pause
