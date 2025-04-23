# 工厂智能管理系统 - Docker部署指南

本文档提供了使用Docker部署工厂智能管理系统的详细说明。

## 系统要求

- Docker 19.03+
- Docker Compose 1.27+
- 至少2GB可用内存
- 至少10GB可用磁盘空间

## 快速开始

### 1. 克隆仓库

```bash
git clone <仓库地址>
cd industry
```

### 2. 构建并启动容器

推荐的启动方式是先启动数据库，然后启动应用：

```bash
# 先启动数据库容器
docker-compose up -d mysql

# 等待数据库初始化完成（第一次启动时可能需要等待约 30 秒）
sleep 30

# 然后启动应用容器
docker-compose up -d app
```

如果数据库初始化有问题，可以使用手动初始化脚本：

```bash
# 给脚本添加执行权限
chmod +x manual-init-db.sh

# 执行手动初始化脚本
./manual-init-db.sh
```

首次启动时，系统将自动执行以下操作：
- 构建应用镜像
- 启动MySQL数据库
- 初始化数据库表结构
- 创建测试账号
- 启动应用服务器

### 3. 访问应用

应用启动后，可通过浏览器访问：

```
http://localhost:3000
```

## 测试账号

- 厂长：SP0001 / admin1
- 工长：FM0002 / foreman123
- 产线工人：WK0008 / worker123
- 安全员：SF0009 / safety123

## 常用命令

### 查看容器状态

```bash
docker-compose ps
```

### 查看应用日志

```bash
docker-compose logs -f app
```

### 查看数据库日志

```bash
docker-compose logs -f mysql
```

### 停止所有服务

```bash
docker-compose down
```

### 重新构建并启动服务

```bash
docker-compose up -d --build
```

### 完全清理（包括数据卷）

```bash
docker-compose down -v
```

## 故障排除

### 数据库连接失败

1. 检查MySQL容器是否正常运行：`docker-compose ps`
2. 查看MySQL日志：`docker-compose logs mysql`
3. 确认环境变量配置正确

### 应用启动失败

1. 查看应用日志：`docker-compose logs app`
2. 检查数据库初始化是否成功
3. 尝试重新构建应用：`docker-compose up -d --build app`

### 数据库初始化问题

1. 检查数据库状态：
   ```bash
   docker exec -it industry-mysql mysql -uroot -pmwYgR7#*X2 -e "USE industry_db; SHOW TABLES;"
   ```

2. 手动初始化数据库：
   ```bash
   ./manual-init-db.sh
   ```

3. 如果数据库已存在但数据不完整，可以先删除数据库然后重新初始化：
   ```bash
   docker exec -it industry-mysql mysql -uroot -pmwYgR7#*X2 -e "DROP DATABASE industry_db;"
   ./manual-init-db.sh
   ```

### 容器一直处于重启状态

1. 停止并删除所有容器：
   ```bash
   docker-compose down
   ```

2. 清理Docker缓存：
   ```bash
   docker system prune -a
   ```

3. 重新构建并启动容器：
   ```bash
   docker-compose build --no-cache
   docker-compose up -d mysql
   sleep 30
   docker-compose up -d app
   ```

### 端口被占用

1. 检查端口占用情况：
   ```bash
   # Windows命令
   netstat -ano | findstr :3000
   netstat -ano | findstr :3306
   ```

2. 修改docker-compose.yml中的端口映射，例如将 3000:3000 改为 3001:3000
