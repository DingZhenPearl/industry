# 数据库操作工具使用说明

本工具将多个数据库操作脚本合并为一个统一的命令行工具，提供了数据库初始化、字段添加、数据迁移、数据查询等功能。

## 功能列表

1. 初始化数据库
2. 添加字段（line_id, machine_id, employee_id, group_id）
3. 数据类型迁移（INT 转 VARCHAR）
4. 验证列类型
5. 获取用户数据
6. 获取团队成员
7. 获取产线信息
8. 验证用户登录
9. 注册新用户
10. 更新用户信息（手机号、用户名、密码、组号）

## 使用方法

### 初始化数据库

```bash
python db_operations.py init
```

### 添加字段

添加产线ID字段：
```bash
python db_operations.py add-field line_id
```

添加机器ID字段：
```bash
python db_operations.py add-field machine_id
```

添加工号字段：
```bash
python db_operations.py add-field employee_id
```

添加组ID字段：
```bash
python db_operations.py add-field group_id
```

### 迁移数据类型

将line_id和machine_id从INT类型转换为VARCHAR类型：
```bash
python db_operations.py migrate
```

### 验证列类型

验证line_id和machine_id的数据类型：
```bash
python db_operations.py verify
```

### 获取用户数据

获取所有用户信息：
```bash
python db_operations.py get-users
```

### 获取团队成员

获取指定组的团队成员：
```bash
python db_operations.py get-team 1
```

### 获取产线信息

获取指定组的产线信息：
```bash
python db_operations.py get-lines 1
```

### 验证用户登录

验证用户登录信息：
```bash
python db_operations.py verify-user username password role
```

### 注册新用户

注册新用户：
```bash
python db_operations.py register username password role
```

### 更新用户信息

更新用户手机号：
```bash
python db_operations.py update-user username role phone
```

更新用户名：
```bash
python db_operations.py update-username current_username role new_username
```

更新密码：
```bash
python db_operations.py update-password username role new_password
```

更新组号：
```bash
python db_operations.py update-group username role group_id
```

## 注意事项

1. 请确保已安装所需的Python依赖：
   ```bash
   pip install mysql-connector-python
   ```

2. 请根据实际情况修改数据库连接信息（host, user, password）。

3. 所有命令的输出均为JSON格式，便于与前端交互。

4. 本工具替代了原有的多个单独脚本，包括：
   - add_line_id.py
   - add_employee_id.py
   - get_users.py
   - verify_user.py
   - migrate_id_columns.py
   - verify_migration.py
   - get_lines.py
   - init_db.py
