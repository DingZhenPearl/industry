#!/bin/sh
set -e

# 设置数据库连接参数
DB_HOST=${1:-mysql}
DB_USER=${2:-root}
DB_PASSWORD=${3:-mwYgR7#*X2}
DB_NAME=${4:-industry_db}

echo "测试数据库连接..."
echo "主机: $DB_HOST"
echo "用户: $DB_USER"
echo "数据库: $DB_NAME"

# 测试数据库连接
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT 1 as connection_test;"

# 检查数据库是否存在
echo "检查数据库是否存在..."
DB_EXISTS=$(mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SHOW DATABASES LIKE '$DB_NAME';" | grep -c $DB_NAME || true)

if [ "$DB_EXISTS" -gt 0 ]; then
    echo "数据库 '$DB_NAME' 已存在"
else
    echo "数据库 '$DB_NAME' 不存在，正在创建..."
    mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "数据库创建成功"
fi

# 检查用户表是否存在
echo "检查用户表是否存在..."
TABLE_EXISTS=$(mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SHOW TABLES FROM $DB_NAME LIKE 'users';" | grep -c users || true)

if [ "$TABLE_EXISTS" -gt 0 ]; then
    echo "用户表已存在"
else
    echo "用户表不存在，正在创建..."
    mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(64) NOT NULL,
        role VARCHAR(20) NOT NULL,
        phone VARCHAR(20),
        status ENUM('在岗', '请假', '离岗') DEFAULT '在岗',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        group_id INT NULL COMMENT '所属分组ID',
        employee_id VARCHAR(20) NULL COMMENT '工号'
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "用户表创建成功"
fi

echo "数据库连接测试完成"
