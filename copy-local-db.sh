#!/bin/bash
# 脚本用于将本地数据库复制到 Docker 容器

# 配置变量
LOCAL_MYSQL_USER="root"
LOCAL_MYSQL_PASSWORD="mwYgR7#*X2"  # 替换为您本地 MySQL 的密码
DOCKER_MYSQL_USER="root"
DOCKER_MYSQL_PASSWORD="mwYgR7#*X2"
DB_NAME="industry_db"
BACKUP_FILE="industry_db_backup.sql"
CONTAINER_NAME="industry-mysql"

# 确保 Docker 已安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 MySQL 容器是否运行
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo "错误: MySQL 容器未运行，请先启动容器"
    echo "运行: docker-compose up -d mysql"
    exit 1
fi

echo "开始从本地数据库导出数据..."

# 导出本地数据库
if command -v mysqldump &> /dev/null; then
    # 如果 mysqldump 在 PATH 中
    mysqldump -u $LOCAL_MYSQL_USER -p$LOCAL_MYSQL_PASSWORD --databases $DB_NAME > $BACKUP_FILE
else
    # 尝试常见的 MySQL 安装路径
    if [ -f "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" ]; then
        "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u $LOCAL_MYSQL_USER -p$LOCAL_MYSQL_PASSWORD --databases $DB_NAME > $BACKUP_FILE
    elif [ -f "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe" ]; then
        "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe" -u $LOCAL_MYSQL_USER -p$LOCAL_MYSQL_PASSWORD --databases $DB_NAME > $BACKUP_FILE
    else
        echo "错误: 找不到 mysqldump 命令，请手动导出数据库"
        exit 1
    fi
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 数据库导出失败，未生成备份文件"
    exit 1
fi

echo "数据库导出成功，文件大小: $(stat -c%s "$BACKUP_FILE") 字节"
echo "将备份文件复制到 Docker 容器..."

# 复制 SQL 文件到容器
docker cp $BACKUP_FILE $CONTAINER_NAME:/tmp/

echo "在 Docker 容器中导入数据..."

# 在容器中执行 SQL 文件
docker exec -i $CONTAINER_NAME mysql -u$DOCKER_MYSQL_USER -p$DOCKER_MYSQL_PASSWORD < $BACKUP_FILE

# 检查导入结果
echo "验证数据导入..."
docker exec -i $CONTAINER_NAME mysql -u$DOCKER_MYSQL_USER -p$DOCKER_MYSQL_PASSWORD -e "USE $DB_NAME; SHOW TABLES;"

echo "数据库复制完成！"
echo "重启应用容器以应用更改: docker-compose restart app"
