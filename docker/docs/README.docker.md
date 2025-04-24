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

```bash
docker-compose up -d
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

## 容器说明

本项目使用Docker Compose编排以下服务：

1. **MySQL数据库 (mysql)**
   - 基于官方MySQL 5.7镜像
   - 数据持久化存储在命名卷中
   - 端口映射：3306:3306

2. **应用服务 (app)**
   - 基于Node.js 14和Python 3
   - 包含前端和后端服务
   - 端口映射：3000:3000

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

## 自定义配置

### 修改数据库密码

1. 编辑`docker-compose.yml`文件，修改`MYSQL_ROOT_PASSWORD`环境变量
2. 同时更新`app`服务的`DB_PASSWORD`环境变量
3. 重新构建并启动服务：`docker-compose up -d --build`

### 修改端口映射

1. 编辑`docker-compose.yml`文件，修改`ports`部分
2. 例如，将应用端口改为8080：`"8080:3000"`
3. 重新启动服务：`docker-compose up -d`

## 故障排除

### 数据库连接失败

1. 检查MySQL容器是否正常运行：`docker-compose ps`
2. 查看MySQL日志：`docker-compose logs mysql`
3. 确认环境变量配置正确

### 应用启动失败

1. 查看应用日志：`docker-compose logs app`
2. 检查数据库初始化是否成功
3. 尝试重新构建应用：`docker-compose up -d --build app`

## 生产环境部署注意事项

1. 修改所有默认密码
2. 配置适当的数据备份策略
3. 考虑使用外部数据库服务
4. 配置HTTPS
5. 限制容器资源使用
