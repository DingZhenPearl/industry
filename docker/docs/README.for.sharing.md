# 工厂智能管理系统 - 部署指南

本文档提供了部署工厂智能管理系统的详细说明。

## 系统要求

- Docker 19.03+
- Docker Compose 1.27+
- 至少2GB可用内存
- 至少10GB可用磁盘空间
- Windows 10/11 或 Linux/macOS

## 快速开始（Windows）

### 自动安装（推荐）

1. 解压收到的文件
2. 双击运行 `install-docker-app.bat`
3. 等待安装完成
4. 打开浏览器访问 http://localhost:3000

### 手动安装

1. 确保Docker和Docker Compose已安装
2. 打开命令提示符或PowerShell，进入解压目录
3. 运行以下命令启动MySQL容器：
   ```
   docker-compose up -d mysql
   ```
4. 等待约1分钟，让MySQL初始化完成
5. 如果有数据库转储文件，导入数据：
   ```
   docker cp full_db_dump.sql industry-mysql:/tmp/
   docker exec -i industry-mysql mysql -uroot -pmwYgR7#*X2 < full_db_dump.sql
   ```
6. 启动应用容器：
   ```
   docker-compose up -d app
   ```
7. 打开浏览器访问 http://localhost:3000

## 快速开始（Linux/macOS）

1. 确保Docker和Docker Compose已安装
2. 打开终端，进入解压目录
3. 运行以下命令启动MySQL容器：
   ```bash
   docker-compose up -d mysql
   ```
4. 等待约1分钟，让MySQL初始化完成
5. 如果有数据库转储文件，导入数据：
   ```bash
   docker cp full_db_dump.sql industry-mysql:/tmp/
   docker exec -i industry-mysql mysql -uroot -pmwYgR7#*X2 < full_db_dump.sql
   ```
6. 启动应用容器：
   ```bash
   docker-compose up -d app
   ```
7. 打开浏览器访问 http://localhost:3000

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

### 重新启动服务

```bash
docker-compose restart
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

### 端口被占用

1. 检查端口占用情况：
   ```
   # Windows命令
   netstat -ano | findstr :3000
   netstat -ano | findstr :3307

   # Linux/macOS命令
   netstat -an | grep 3000
   netstat -an | grep 3307
   ```

2. 修改docker-compose.yml中的端口映射，例如将 3000:3000 改为 3001:3000

## 备份数据

如果您需要备份数据库数据，可以使用以下命令：

```bash
docker exec -i industry-mysql mysqldump -uroot -pmwYgR7#*X2 --databases industry_db > backup.sql
```

## 恢复数据

如果您需要恢复数据库数据，可以使用以下命令：

```bash
docker exec -i industry-mysql mysql -uroot -pmwYgR7#*X2 < backup.sql
```

## 联系方式

如有任何问题或需要技术支持，请联系：

- 邮箱：[您的邮箱]
- 电话：[您的电话]
