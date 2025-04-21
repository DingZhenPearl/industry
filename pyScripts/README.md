# Python脚本部分说明文档

## 概述

Python脚本部分是工厂智能管理系统的数据处理层，主要负责与数据库的直接交互、数据处理和业务逻辑实现。这些脚本通过Node.js服务器调用，为前端提供数据支持。

## 目录结构

```
pyScripts/
├── init_db.py                    # 数据库初始化脚本
├── user_data_operations.py       # 用户数据操作脚本
├── production_line_unified.py    # 产线管理统一工具
├── equipment_unified.py          # 设备管理统一工具
├── workorder_manager.py          # 工单管理脚本
├── employee_status_manager.py    # 员工状态管理脚本
└── simulate_monitoring_data.py   # 监控数据模拟脚本
```

## 核心功能

### 1. 数据库初始化 (init_db.py)

- 创建数据库和所需表结构
- 初始化基础数据
- 添加测试账号

### 2. 用户数据操作 (user_data_operations.py)

- 用户认证：验证用户登录凭据
- 用户注册：创建新用户账号
- 用户查询：获取用户列表、工长列表等
- 用户更新：修改用户信息、密码等
- 班组管理：分配用户到班组

主要命令：
- `verify-user`: 通过用户名验证用户
- `verify-user-by-id`: 通过工号验证用户
- `register`: 注册新用户
- `get-users`: 获取所有用户
- `get-foremen`: 获取所有工长
- `get-team`: 获取班组成员
- `update-user`: 更新用户信息
- `update-group`: 更新用户班组

### 3. 产线管理 (production_line_unified.py)

- 产线表管理：创建和维护产线相关表
- 产线信息管理：添加、更新、删除产线
- 产线状态管理：更新和查询产线状态
- 产线与工长关联：分配工长负责产线
- 产线查询：按组号、工长等条件查询产线

主要命令：
- `create-tables`: 创建产线相关表
- `add-line`: 添加新产线
- `update-status`: 更新产线状态
- `list`: 获取产线列表
- `list-by-foreman`: 获取工长负责的产线
- `list-by-group`: 获取班组的产线
- `get-with-status`: 获取产线及其最新状态
- `get-with-foremen`: 获取产线及其负责工长

### 4. 设备管理 (equipment_unified.py)

- 设备表管理：创建和维护设备相关表
- 设备信息管理：添加、更新、删除设备
- 设备状态管理：更新和查询设备状态
- 设备与工人关联：分配工人负责设备
- 设备查询：按产线、状态等条件查询设备

主要命令：
- `create-tables`: 创建设备相关表
- `add-equipment`: 添加新设备
- `update-status`: 更新设备状态
- `list`: 获取设备列表
- `get-with-status`: 获取设备及其最新状态
- `get-with-workers`: 获取设备及其负责工人
- `update-sensor-projects`: 更新设备传感器项目

### 5. 工单管理 (workorder_manager.py)

- 工单表管理：创建和维护工单相关表
- 工单创建：生成新工单
- 工单分配：分配工单给工长或班组
- 工单状态更新：更新工单进度和状态
- 工单查询：按状态、班组等条件查询工单

主要功能：
- 创建工单表
- 添加新工单
- 更新工单状态
- 获取工单列表
- 获取单个工单详情

### 6. 员工状态管理 (employee_status_manager.py)

- 考勤记录：上班打卡、下班打卡
- 员工状态更新：更新员工在岗状态
- 考勤查询：获取员工考勤记录

主要命令：
- `check-in`: 上班打卡
- `check-out`: 下班打卡
- `update-status`: 更新员工状态
- `get-records`: 获取考勤记录

### 7. 监控数据模拟 (simulate_monitoring_data.py)

- 模拟设备传感器数据：温度、振动、电流等
- 模拟产线状态数据：产能、噪音、环境温度等
- 定时更新数据库中的状态信息

主要功能：
- 生成模拟的设备状态数据
- 生成模拟的产线状态数据
- 定时更新数据库中的状态信息

## 技术栈

- **Python 3.7+**: 脚本语言
- **mysql-connector-python**: MySQL数据库连接器
- **JSON**: 数据交换格式
- **argparse**: 命令行参数解析

## 与其他部分的交互

- **与服务器交互**: 通过标准输出返回JSON格式的结果，由Node.js服务器解析
- **与数据库交互**: 直接连接MySQL数据库，执行SQL查询和更新操作
- **与前端交互**: 通过服务器间接与前端交互，提供数据支持
