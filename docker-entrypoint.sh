#!/bin/sh
set -e

# 等待MySQL服务就绪
echo "等待MySQL服务就绪..."
sleep 10

# 使用测试脚本测试数据库连接
echo "测试数据库连接..."
/app/test-db-connection.sh $DB_HOST $DB_USER $DB_PASSWORD $DB_NAME 3308
echo "MySQL服务已就绪!"

# 等待初始化脚本执行完成
echo "等待数据库初始化脚本执行完成..."
sleep 5

# 修改Python脚本中的数据库连接信息
echo "更新Python脚本中的数据库连接配置..."
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/host='localhost'/host='$DB_HOST'/g" {} \;
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/user='root'/user='$DB_USER'/g" {} \;
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/password='mwYgR7#\*X2'/password='$DB_PASSWORD'/g" {} \;
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/database='industry_db'/database='$DB_NAME'/g" {} \;

# 运行详细的数据库状态检查
echo "运行详细的数据库状态检查..."
/app/check-db-status.sh $DB_HOST $DB_USER $DB_PASSWORD $DB_NAME 3308

# 检查是否需要初始化测试数据
USER_COUNT=$(mysql -h $DB_HOST -P 3308 -u $DB_USER -p$DB_PASSWORD -N -e "SELECT COUNT(*) FROM $DB_NAME.users;" 2>/dev/null || echo "0")

if [ "$USER_COUNT" -lt "4" ]; then
  echo "用户数据不足，可能需要手动初始化测试数据"
  echo "请确保 init-db.sql 文件已正确挂载到 MySQL 容器中"
fi

echo "数据库状态检查完成"

# 启动后端服务器
echo "启动应用服务器..."
exec node /app/server/index.js
