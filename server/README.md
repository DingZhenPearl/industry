# 服务器部分说明文档

## 概述

服务器部分是工厂智能管理系统的后端，基于Node.js和Express框架构建，主要负责处理前端请求、与数据库交互以及调用Python脚本进行数据处理。

## 目录结构

```
server/
├── index.js                # 服务器入口文件
├── middleware.js           # 中间件配置
├── routes/                 # 路由处理
│   ├── auth.js             # 认证相关路由
│   ├── users.js            # 用户管理路由
│   ├── workorders.js       # 工单管理路由
│   ├── equipment.js        # 设备管理路由
│   ├── production_line.js  # 产线管理路由
│   └── attendance.js       # 考勤管理路由
└── utils/                  # 工具函数
    ├── pythonRunner.js     # Python脚本执行器
    └── uidGenerator.js     # 用户唯一标识生成器
```

## 核心功能

### 1. 服务器配置 (index.js)

- 创建Express应用实例
- 配置中间件
- 注册API路由
- 处理Vue路由（SPA应用支持）
- 启动HTTP服务器

### 2. 中间件 (middleware.js)

- CORS配置：允许前端跨域请求
- 请求体解析：处理JSON格式的请求体
- 会话管理：使用express-session管理用户会话
- 静态文件服务：提供前端构建文件
- 认证中间件：验证用户登录状态
- UID中间件：验证用户唯一标识

### 3. 路由模块

#### 认证路由 (auth.js)
- 用户登录：验证用户凭据并创建会话
- 用户注册：创建新用户账号
- 用户登出：销毁用户会话

#### 用户管理路由 (users.js)
- 获取用户列表
- 获取工长列表
- 获取班组成员
- 获取工长分配的产线
- 更新用户信息

#### 工单管理路由 (workorders.js)
- 创建工单
- 获取工单列表
- 更新工单状态
- 分配工单给工长或班组
- 提交工单完成报告

#### 设备管理路由 (equipment.js)
- 获取设备列表
- 获取设备详情及状态
- 添加新设备
- 更新设备状态
- 分配工人负责设备
- 更新设备传感器配置

#### 产线管理路由 (production_line.js)
- 获取产线列表
- 获取产线详情及状态
- 添加新产线
- 更新产线状态
- 分配工长负责产线

#### 考勤管理路由 (attendance.js)
- 上班打卡
- 下班打卡
- 获取考勤记录
- 更新员工状态

### 4. 工具函数

#### Python脚本执行器 (pythonRunner.js)
- 使用Node.js的child_process模块调用Python脚本
- 处理脚本输出并解析为JSON格式
- 提供调试选项，便于开发调试

#### 用户唯一标识生成器 (uidGenerator.js)
- 根据用户工号生成唯一标识符
- 验证用户唯一标识符的有效性

## 技术栈

- **Node.js**: JavaScript运行时环境
- **Express**: Web应用框架
- **express-session**: 会话管理
- **cors**: 跨域资源共享
- **body-parser**: 请求体解析

## 与其他部分的交互

- **与前端交互**: 通过RESTful API接收请求并返回JSON格式的响应
- **与Python脚本交互**: 通过子进程调用Python脚本，处理数据库操作和复杂业务逻辑
- **与数据库交互**: 通过Python脚本间接与MySQL数据库交互
