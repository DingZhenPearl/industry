@echo off
echo 正在将本地数据库导入到 Docker 容器...

REM 设置参数
set MYSQL_CONTAINER=industry-mysql
set IMPORT_FILE=local_db_dump.sql
set MYSQL_PORT=3308

REM 检查导出文件是否存在
if not exist %IMPORT_FILE% (
    echo 错误: 导出文件 %IMPORT_FILE% 不存在
    echo 请先运行 export-local-db.bat 导出本地数据库
    exit /b 1
)

REM 检查 Docker 容器是否运行
docker ps | findstr %MYSQL_CONTAINER% > nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: MySQL 容器未运行
    echo 请确保 Docker 容器已启动: docker-compose up -d mysql
    exit /b 1
)

REM 将导出文件复制到容器
echo 复制数据库导出文件到容器...
docker cp %IMPORT_FILE% %MYSQL_CONTAINER%:/tmp/%IMPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo 错误: 无法将文件复制到容器
    exit /b 1
)

REM 在容器中执行导入
echo 在容器中执行数据库导入...
docker exec -i %MYSQL_CONTAINER% mysql -uroot -pmwYgR7#*X2 -P %MYSQL_PORT% < %IMPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo 错误: 数据库导入失败
    exit /b 1
)

echo 数据库导入成功！
echo.
echo 现在您可以启动应用容器: docker-compose up -d app
