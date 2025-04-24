# Docker 部署说明

本项目支持使用Docker进行容器化部署。所有Docker相关文件已整理到`docker`目录中。

## 快速开始

### 使用图形界面管理Docker

运行`docker-manager.bat`脚本，通过菜单选择操作：

```
docker-manager.bat
```

### 命令行操作

1. **启动容器**：
   ```
   docker-start.bat
   ```

2. **停止容器**：
   ```
   docker-stop.bat
   ```

3. **导出数据库**：
   ```
   docker\scripts\export-db-only.bat
   ```

4. **创建共享包**：
   ```
   docker\scripts\create-sharing-package.bat
   ```

## 目录结构

Docker相关文件已整理到以下目录结构：

```
docker/
├── config/             # Docker配置文件
│   ├── docker-compose.yml  # Docker Compose配置
│   └── Dockerfile          # 应用镜像构建文件
│
├── scripts/            # 脚本文件
│   ├── 部署脚本
│   ├── 数据库管理
│   └── 共享与分发
│
└── docs/               # 文档
```

详细说明请参阅 [docker/README.md](docker/README.md)。
