#!/bin/sh
set -e

# 设置数据库连接参数
DB_HOST=${1:-mysql}
DB_USER=${2:-root}
DB_PASSWORD=${3:-mwYgR7#*X2}
DB_NAME=${4:-industry_db}
DB_PORT=${5:-3308}

echo "检查数据库状态..."
echo "主机: $DB_HOST"
echo "用户: $DB_USER"
echo "数据库: $DB_NAME"
echo "端口: $DB_PORT"

# 检查数据库是否存在
echo "检查数据库是否存在..."
DB_EXISTS=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -e "SHOW DATABASES LIKE '$DB_NAME';" | grep -c $DB_NAME || true)

if [ "$DB_EXISTS" -gt 0 ]; then
    echo "数据库 '$DB_NAME' 已存在"
else
    echo "数据库 '$DB_NAME' 不存在，请检查初始化脚本是否正确执行"
    exit 1
fi

# 检查表是否存在
echo "检查表是否存在..."
TABLES=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -e "SHOW TABLES FROM $DB_NAME;")
echo "$TABLES"

# 检查各表中的记录数
echo "检查各表中的记录数..."

# 用户表
USER_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -N -e "SELECT COUNT(*) FROM $DB_NAME.users;" 2>/dev/null || echo "表不存在")
echo "用户表: $USER_COUNT 条记录"

# 产线表
LINE_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -N -e "SELECT COUNT(*) FROM $DB_NAME.production_line;" 2>/dev/null || echo "表不存在")
echo "产线表: $LINE_COUNT 条记录"

# 设备表
EQUIP_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -N -e "SELECT COUNT(*) FROM $DB_NAME.equipment;" 2>/dev/null || echo "表不存在")
echo "设备表: $EQUIP_COUNT 条记录"

# 工单表
WORKORDER_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -N -e "SELECT COUNT(*) FROM $DB_NAME.workorders;" 2>/dev/null || echo "表不存在")
echo "工单表: $WORKORDER_COUNT 条记录"

# 检查测试用户是否存在
echo "检查测试用户是否存在..."
TEST_USERS=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -N -e "SELECT username, role FROM $DB_NAME.users;" 2>/dev/null || echo "表不存在")
echo "$TEST_USERS"

echo "数据库状态检查完成"
