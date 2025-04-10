# 服务器代码结构说明

本服务器代码采用模块化结构，按照功能进行拆分，提高了代码的可维护性和可读性。

## 目录结构

```
server/
├── index.js           # 主服务器文件，负责引入模块和启动服务器
├── middleware.js      # 中间件配置文件
├── routes/            # 路由模块目录
│   ├── auth.js        # 认证相关路由（登录、注册、退出登录）
│   ├── users.js       # 用户管理路由（获取和更新用户信息）
│   └── foreman.js     # 工长相关路由（获取团队成员和产线信息）
└── utils/             # 工具函数目录
    └── pythonRunner.js # Python脚本执行工具
```

## 功能模块说明

### 主服务器文件 (index.js)

负责引入各个模块，设置中间件，注册路由，并启动服务器。

### 中间件配置 (middleware.js)

包含所有中间件的配置，如CORS、请求体解析、会话管理等，以及认证中间件。

### 认证路由 (routes/auth.js)

处理用户认证相关的功能：
- 登录
- 注册
- 获取当前用户信息
- 退出登录

### 用户管理路由 (routes/users.js)

处理用户信息管理相关的功能：
- 获取所有用户列表
- 更新用户名
- 更新密码
- 更新手机号
- 更新用户信息
- 更新用户组号

### 工长相关路由 (routes/foreman.js)

处理工长特定的功能：
- 获取工长团队成员列表
- 获取工长分配的产线列表

### Python脚本执行工具 (utils/pythonRunner.js)

提供了一个通用的函数，用于执行Python脚本并处理其输出，简化了代码重复。

## 使用说明

1. 启动服务器：
```
node server/index.js
```

2. 服务器默认运行在 http://localhost:3000

3. API路径前缀为 `/api`，例如：
   - 登录：`POST /api/login`
   - 获取用户列表：`GET /api/users`
   - 获取工长团队成员：`GET /api/foreman/team-members?group_id=1`
