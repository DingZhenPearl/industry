@echo off
chcp 936 > nul
echo Starting to copy local database to Docker container...

REM Setting parameters
set MYSQL_USER=root
set MYSQL_PASSWORD=mwYgR7#*X2
set MYSQL_DATABASE=industry_db
set EXPORT_FILE=full_db_dump.sql
set MYSQL_CONTAINER=industry-mysql
set DOCKER_MYSQL_PORT=3308

echo ======================================================
echo Step 1: Preparing Docker environment
echo ======================================================
echo Stopping any running containers...
docker-compose down

echo Removing old MySQL data volume...
docker volume rm industry_mysql-data 2>nul

echo Starting MySQL container with MySQL 8.0...
docker-compose up -d mysql

echo Waiting for container to start and initialize (this may take a minute)...
echo This is especially important for first-time setup with MySQL 8.0
timeout /t 60 /nobreak > nul

REM Check if container is running
docker ps | findstr %MYSQL_CONTAINER% > nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Cannot start MySQL container
    exit /b 1
)

echo MySQL container started successfully

echo ======================================================
echo Step 2: Exporting local database
echo ======================================================
echo Exporting database %MYSQL_DATABASE% to file %EXPORT_FILE%...

REM Try to export database using mysqldump
mysqldump -u%MYSQL_USER% -p%MYSQL_PASSWORD% --databases %MYSQL_DATABASE% --add-drop-database --routines --events --triggers > %EXPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo Trying with full path...

    REM Try common MySQL installation paths
    if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" (
        "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u%MYSQL_USER% -p%MYSQL_PASSWORD% --databases %MYSQL_DATABASE% --add-drop-database --routines --events --triggers > %EXPORT_FILE%
    ) else if exist "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe" (
        "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe" -u%MYSQL_USER% -p%MYSQL_PASSWORD% --databases %MYSQL_DATABASE% --add-drop-database --routines --events --triggers > %EXPORT_FILE%
    ) else (
        echo Error: Cannot find mysqldump command
        exit /b 1
    )

    if %ERRORLEVEL% NEQ 0 (
        echo Error: Database export failed
        exit /b 1
    )
)

if not exist %EXPORT_FILE% (
    echo Error: Export file %EXPORT_FILE% was not generated
    exit /b 1
)

echo Database exported successfully! File: %EXPORT_FILE%

echo ======================================================
echo Step 3: Copying export file to container
echo ======================================================
echo Copying database export file to container...
docker cp %EXPORT_FILE% %MYSQL_CONTAINER%:/tmp/%EXPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo Error: Cannot copy file to container
    exit /b 1
)

echo ======================================================
echo Step 4: Importing database in container
echo ======================================================
echo Executing database import in container...

REM Delete existing database if it exists
echo Deleting existing database in container (if exists)...
docker exec -i %MYSQL_CONTAINER% mysql -uroot -pmwYgR7#*X2 -P %DOCKER_MYSQL_PORT% -e "DROP DATABASE IF EXISTS %MYSQL_DATABASE%;"

if %ERRORLEVEL% NEQ 0 (
    echo Warning: Cannot delete existing database, will try direct import
)

REM Execute import
docker exec -i %MYSQL_CONTAINER% mysql -uroot -pmwYgR7#*X2 -P %DOCKER_MYSQL_PORT% < %EXPORT_FILE%

if %ERRORLEVEL% NEQ 0 (
    echo Error: Database import failed
    exit /b 1
)

echo ======================================================
echo Step 5: Verifying import results
echo ======================================================
echo Checking database tables...
docker exec -i %MYSQL_CONTAINER% mysql -uroot -pmwYgR7#*X2 -P %DOCKER_MYSQL_PORT% -e "USE %MYSQL_DATABASE%; SHOW TABLES;"

echo Checking user data...
docker exec -i %MYSQL_CONTAINER% mysql -uroot -pmwYgR7#*X2 -P %DOCKER_MYSQL_PORT% -e "USE %MYSQL_DATABASE%; SELECT COUNT(*) AS user_count FROM users;"

echo Checking production line data...
docker exec -i %MYSQL_CONTAINER% mysql -uroot -pmwYgR7#*X2 -P %DOCKER_MYSQL_PORT% -e "USE %MYSQL_DATABASE%; SELECT COUNT(*) AS line_count FROM production_line;"

echo Checking equipment data...
docker exec -i %MYSQL_CONTAINER% mysql -uroot -pmwYgR7#*X2 -P %DOCKER_MYSQL_PORT% -e "USE %MYSQL_DATABASE%; SELECT COUNT(*) AS equipment_count FROM equipment;"

echo ======================================================
echo Step 6: Restarting application container
echo ======================================================
echo Do you want to restart the application container to apply changes? (Y/N)
set /p RESTART=

if /i "%RESTART%"=="Y" (
    echo Restarting application container...
    docker-compose restart app
    echo Application container restarted
) else (
    echo Skipping application container restart
    echo You can restart it manually later: docker-compose restart app
)

echo ======================================================
echo Database copy completed!
echo ======================================================
echo Local database has been successfully copied to Docker container
echo You can now access the application at: http://localhost:3000
