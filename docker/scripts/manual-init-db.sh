#!/bin/bash
# 手动初始化数据库脚本

# 确保 Docker 已安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 确保 Docker Compose 已安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查 MySQL 容器是否运行
MYSQL_CONTAINER=$(docker-compose ps -q mysql)
if [ -z "$MYSQL_CONTAINER" ]; then
    echo "错误: MySQL 容器未运行，请先启动容器"
    echo "运行: docker-compose up -d mysql"
    exit 1。
fi

echo "正在手动初始化数据库..."

# 将 SQL 文件复制到容器中
echo "复制 SQL 文件到容器..."
docker cp init-db.sql $MYSQL_CONTAINER:/tmp/init-db.sql

# 在容器中执行 SQL 文件
echo "执行 SQL 文件..."
docker exec -i $MYSQL_CONTAINER sh -c 'mysql -uroot -pmwYgR7#*X2 < /tmp/init-db.sql'

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "数据库初始化成功!"
else
    echo "错误: 数据库初始化失败"
    exit 1
fi

# 检查数据库状态
echo "检查数据库状态..."
docker exec -i $MYSQL_CONTAINER sh -c 'mysql -uroot -pmwYgR7#*X2 -e "USE industry_db; SHOW TABLES;"'

echo "检查表中的数据..."
docker exec -i $MYSQL_CONTAINER sh -c 'mysql -uroot -pmwYgR7#*X2 -e "USE industry_db; SELECT COUNT(*) AS 用户数 FROM users; SELECT COUNT(*) AS 产线数 FROM production_line; SELECT COUNT(*) AS 设备数 FROM equipment; SELECT COUNT(*) AS 工单数 FROM workorders;"'

echo "数据库初始化完成"
echo "现在可以启动应用容器: docker-compose up -d app"
