@echo off
chcp 936 > nul
title Docker管理工具

:menu
cls
echo ======================================================
echo                Docker管理工具
echo ======================================================
echo.
echo  [1] 启动Docker容器
echo  [2] 停止Docker容器
echo  [3] 查看容器状态
echo  [4] 查看应用日志
echo  [5] 查看数据库日志
echo  [6] 导出数据库
echo  [7] 创建共享包
echo  [8] 重新构建容器
echo  [9] 退出
echo.
echo ======================================================

set /p choice=请选择操作 [1-9]: 

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto status
if "%choice%"=="4" goto app_logs
if "%choice%"=="5" goto db_logs
if "%choice%"=="6" goto export_db
if "%choice%"=="7" goto create_package
if "%choice%"=="8" goto rebuild
if "%choice%"=="9" goto exit
goto menu

:start
cls
echo 正在启动Docker容器...
call docker-start.bat
goto menu

:stop
cls
echo 正在停止Docker容器...
call docker-stop.bat
goto menu

:status
cls
echo 正在查看容器状态...
cd docker\config
docker-compose ps
cd ..\..
pause
goto menu

:app_logs
cls
echo 正在查看应用日志...
cd docker\config
docker-compose logs -f app
cd ..\..
goto menu

:db_logs
cls
echo 正在查看数据库日志...
cd docker\config
docker-compose logs -f mysql
cd ..\..
goto menu

:export_db
cls
echo 正在导出数据库...
call docker\scripts\export-db-only.bat
goto menu

:create_package
cls
echo 正在创建共享包...
call docker\scripts\create-sharing-package.bat
goto menu

:rebuild
cls
echo 正在重新构建容器...
cd docker\config
docker-compose down
docker-compose up -d --build
cd ..\..
echo 容器已重新构建并启动！
pause
goto menu

:exit
exit
