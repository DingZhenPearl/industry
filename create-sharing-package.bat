@echo off
chcp 936 > nul
echo 正在创建共享包...

REM 设置参数
set PACKAGE_DIR=industry-system-package
set MYSQL_CONTAINER=industry-mysql
set EXPORT_FILE=full_db_dump.sql

echo ======================================================
echo 步骤1: 准备目录
echo ======================================================
if exist "%PACKAGE_DIR%" (
    echo 清理旧的包目录...
    rmdir /s /q "%PACKAGE_DIR%"
)
mkdir "%PACKAGE_DIR%"

echo ======================================================
echo 步骤2: 导出数据库
echo ======================================================
echo 检查MySQL容器是否运行...
docker ps | findstr %MYSQL_CONTAINER% > nul
if %ERRORLEVEL% NEQ 0 (
    echo 警告: MySQL容器未运行，跳过数据库导出
) else (
    echo 正在从Docker容器导出数据库...
    docker exec -i %MYSQL_CONTAINER% mysqldump -uroot -pmwYgR7#*X2 --databases industry_db --add-drop-database --routines --events --triggers > "%PACKAGE_DIR%\%EXPORT_FILE%"

    if %ERRORLEVEL% NEQ 0 (
        echo 警告: 数据库导出可能未完全成功，但将继续创建包
    ) else (
        echo 数据库导出成功！
    )
)

echo ======================================================
echo 步骤3: 复制必要文件
echo ======================================================
echo 复制Docker配置文件...
copy docker-compose.yml "%PACKAGE_DIR%\"
copy Dockerfile "%PACKAGE_DIR%\"

echo 复制安装脚本...
copy install-docker-app.bat "%PACKAGE_DIR%\"

echo 复制README文件...
copy README.for.sharing.md "%PACKAGE_DIR%\README.md"

echo 复制初始化SQL文件...
if exist "init-db.sql" copy init-db.sql "%PACKAGE_DIR%\"

echo 复制其他必要文件...
if exist "docker-entrypoint.sh" copy docker-entrypoint.sh "%PACKAGE_DIR%\"
if exist "test-db-connection.sh" copy test-db-connection.sh "%PACKAGE_DIR%\"
if exist "check-db-status.sh" copy check-db-status.sh "%PACKAGE_DIR%\"

echo ======================================================
echo 步骤4: 导出Docker镜像
echo ======================================================
echo 是否要导出Docker镜像? 这将创建较大的文件，但接收方不需要构建镜像 (Y/N)
set /p EXPORT_IMAGES=

if /i "%EXPORT_IMAGES%"=="Y" (
    echo 正在导出应用镜像...
    docker save -o "%PACKAGE_DIR%\industry-app.tar" industry-app

    echo 正在导出MySQL镜像...
    docker save -o "%PACKAGE_DIR%\mysql-8.0.tar" mysql:8.0

    echo 镜像导出完成！
) else (
    echo 跳过镜像导出，接收方将需要自行构建镜像
)

echo ======================================================
echo 步骤5: 创建压缩包
echo ======================================================
echo 是否要创建ZIP压缩包? (Y/N)
set /p CREATE_ZIP=

if /i "%CREATE_ZIP%"=="Y" (
    echo 正在创建ZIP压缩包...
    powershell -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'industry-system-package.zip' -Force"

    if %ERRORLEVEL% NEQ 0 (
        echo 警告: 创建ZIP压缩包失败，请手动压缩 %PACKAGE_DIR% 目录
    ) else (
        echo ZIP压缩包创建成功: industry-system-package.zip
    )
) else (
    echo 跳过创建ZIP压缩包
)

echo ======================================================
echo 共享包创建完成！
echo ======================================================
echo 共享包已准备好，位于 "%PACKAGE_DIR%" 目录
if /i "%CREATE_ZIP%"=="Y" echo 或者使用ZIP文件: industry-system-package.zip
echo.
echo 请将此包分享给其他人，他们只需运行 install-docker-app.bat 即可部署系统
pause
