# 产线管理工具使用说明

本工具用于创建和管理产线信息表和产线状态表，支持产线静态信息的存储和实时状态数据的记录。

## 功能列表

1. 创建产线相关数据表
2. 添加新产线
3. 更新产线状态
4. 获取产线列表
5. 获取产线状态数据
6. 获取产线及其最新状态信息

## 数据表结构

### 产线静态信息表（production_line）

- `id` INT - 主键
- `line_name` VARCHAR(100) - 产线名称
- `equipment_list` JSON - 包括的设备列表
- `theoretical_capacity` FLOAT - 理论产能
- `status` VARCHAR(20) - 运行状态（正常/维修中/停机/故障等）
- `created_at` TIMESTAMP - 创建时间
- `updated_at` TIMESTAMP - 更新时间

### 产线实时状态表（production_line_status）

- `id` INT - 主键
- `line_id` INT - 产线ID（外键关联production_line表）
- `runtime_hours` FLOAT - 运行时长（小时）
- `real_time_capacity` FLOAT - 产线实时产能
- `collection_time` TIMESTAMP - 数据采集时间

## 使用方法

### 创建产线相关表

```bash
python production_line_manager.py create-tables
```

如需删除现有表后重新创建：
```bash
python production_line_manager.py create-tables --drop
```

### 添加新产线

```bash
python production_line_manager.py add-line --data '{"line_name": "一号生产线", "equipment_list": ["注塑机A-01", "压铸机B-02", "检测仪C-01"], "theoretical_capacity": 1000, "status": "正常"}'
```

### 更新产线状态

```bash
python production_line_manager.py update-status --line-id 1 --data '{"runtime_hours": 126.5, "real_time_capacity": 850}'
```

### 获取产线列表

```bash
python production_line_manager.py list
```

### 获取产线状态

获取最新状态：
```bash
python production_line_manager.py get-status --line-id 1
```

获取多条状态记录：
```bash
python production_line_manager.py get-status --line-id 1 --limit 5
```

### 获取产线及其最新状态

```bash
python production_line_manager.py get-with-status
```

## 注意事项

1. 请确保已安装所需的Python依赖：
   ```bash
   pip install mysql-connector-python
   ```

2. 请根据实际情况修改数据库连接信息（host, user, password）。

3. 所有命令的输出均为JSON格式，便于与前端交互。

4. `equipment_list`字段使用JSON格式存储，可以灵活存储产线包含的设备列表。

5. 产线状态表与产线表通过`line_id`外键关联，删除产线时会级联删除相关的状态记录。
