@echo off
echo 正在导出本地数据库...

REM 设置MySQL连接参数
set MYSQL_USER=root
set MYSQL_PASSWORD=mwYgR7#*X2
set MYSQL_DATABASE=industry_db
set EXPORT_FILE=local_db_dump.sql

REM 导出数据库结构和数据
echo 导出数据库 %MYSQL_DATABASE% 到文件 %EXPORT_FILE%...
mysqldump -u%MYSQL_USER% -p%MYSQL_PASSWORD% --databases %MYSQL_DATABASE% --add-drop-database --routines --events --triggers > %EXPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo 错误: 数据库导出失败
    exit /b 1
)

echo 数据库导出成功！文件: %EXPORT_FILE%
echo.
echo 现在您可以运行 import-to-docker.bat 将数据导入到 Docker 容器中
