# Docker 部署与管理

本目录包含工厂智能管理系统的Docker相关文件，用于容器化部署和管理。

## 目录结构

```
docker/
├── config/             # Docker配置文件
│   ├── docker-compose.yml  # Docker Compose配置
│   └── Dockerfile          # 应用镜像构建文件
│
├── scripts/            # 脚本文件
│   ├── 部署脚本/
│   │   ├── docker-entrypoint.sh    # 容器入口点脚本
│   │   ├── test-db-connection.sh   # 数据库连接测试脚本
│   │   └── check-db-status.sh      # 数据库状态检查脚本
│   │
│   ├── 数据库管理/
│   │   ├── copy-db-to-docker.bat   # 将本地数据库复制到Docker
│   │   ├── export-db-only.bat      # 仅导出数据库
│   │   ├── export-local-db.bat     # 导出本地数据库
│   │   ├── import-to-docker.bat    # 导入数据库到Docker
│   │   ├── copy-local-db.sh        # Linux/Mac版本的数据库复制脚本
│   │   └── Copy-LocalDB.ps1        # PowerShell版本的数据库复制脚本
│   │
│   └── 共享与分发/
│       ├── create-sharing-package.bat  # 创建共享包
│       └── install-docker-app.bat      # 安装应用脚本
│
└── docs/               # 文档
    ├── README.docker.md        # Docker部署指南
    ├── README.for.sharing.md   # 共享版本的README
    └── Docker使用说明.md        # 中文Docker使用说明
```

## 快速开始

### 开发环境

1. 构建并启动容器：
   ```bash
   cd docker/config
   docker-compose up -d
   ```

2. 查看容器状态：
   ```bash
   docker-compose ps
   ```

3. 查看应用日志：
   ```bash
   docker-compose logs -f app
   ```

### 数据库管理

1. 将本地数据库复制到Docker：
   ```bash
   cd docker/scripts
   ./copy-db-to-docker.bat
   ```

2. 仅导出数据库：
   ```bash
   cd docker/scripts
   ./export-db-only.bat
   ```

### 共享与分发

1. 创建共享包：
   ```bash
   cd docker/scripts
   ./create-sharing-package.bat
   ```

2. 安装共享的应用：
   ```bash
   cd <共享包目录>
   ./install-docker-app.bat
   ```

## 详细文档

- [Docker部署指南](docs/README.docker.md)
- [共享版本说明](docs/README.for.sharing.md)
- [中文Docker使用说明](docs/Docker使用说明.md)
