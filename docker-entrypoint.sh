#!/bin/sh
set -e

# 等待MySQL服务就绪
echo "等待MySQL服务就绪..."
until mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT 1"; do
  echo "MySQL服务尚未就绪 - 等待..."
  sleep 2
done
echo "MySQL服务已就绪!"

# 修改Python脚本中的数据库连接信息
echo "更新Python脚本中的数据库连接配置..."
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/host='localhost'/host='$DB_HOST'/g" {} \;
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/user='root'/user='$DB_USER'/g" {} \;
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/password='mwYgR7#\*X2'/password='$DB_PASSWORD'/g" {} \;
find /app/pyScripts -name "*.py" -type f -exec sed -i "s/database='industry_db'/database='$DB_NAME'/g" {} \;

# 初始化数据库
echo "初始化数据库..."
python3 /app/pyScripts/user_data_operations.py init

# 创建设备表
echo "创建设备表..."
python3 /app/pyScripts/equipment_unified.py create-tables

# 创建产线表
echo "创建产线表..."
python3 /app/pyScripts/production_line_unified.py create-tables

# 创建工单表
echo "创建工单表..."
python3 /app/pyScripts/workorder_manager.py create-tables

# 创建考勤表
echo "创建考勤表..."
python3 /app/pyScripts/employee_status_manager.py create-tables

# 启动后端服务器
echo "启动应用服务器..."
exec node /app/server/index.js
