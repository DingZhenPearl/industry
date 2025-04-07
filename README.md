# 工厂智能管理系统

## 项目结构
```
├── pyScripts/          # Python数据库操作脚本
├── server/             # Node.js后端服务器
└── src/                # Vue前端代码
```

## 环境要求
- Node.js 14+
- Python 3.7+
- MySQL 5.7+

## 安装步骤

### 1. 安装Python依赖
```bash
pip install mysql-connector-python
```

### 2. 配置数据库
1. 确保MySQL服务已启动
2. 修改 `pyScripts/verify_user.py` 和 `pyScripts/init_db.py` 中的数据库连接信息
3. 初始化数据库：
```bash
python pyScripts/init_db.py
```

### 3. 安装并启动Node.js服务器
```bash
cd server
npm install
npm run dev
```

### 4. 安装并启动Vue前端
```bash
npm install
npm run dev
```

## 测试账号
- 厂长：admin / admin123
- 工长：foreman1 / foreman123
- 产线工人：worker1 / worker123
- 安全员：safety1 / safety123

## 功能说明
- 支持多角色登录系统
- 使用Session进行身份验证
- 密码加密存储
- 自动根据角色跳转到对应页面
