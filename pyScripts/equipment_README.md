# 设备管理工具使用说明

本工具用于创建和管理设备信息表和设备状态表，支持设备静态信息的存储和实时状态数据的记录。

## 功能列表

1. 创建设备相关数据表
2. 添加新设备
3. 更新设备状态
4. 获取设备列表（支持按产线和状态筛选）
5. 获取设备状态数据
6. 获取设备及其最新状态信息

## 数据表结构

### 设备静态信息表（equipment）

- `id` INT - 主键
- `equipment_name` VARCHAR(100) - 设备名称
- `equipment_code` VARCHAR(50) - 设备唯一编码
- `line_id` VARCHAR(50) - 所属产线ID
- `equipment_type` VARCHAR(50) - 设备类型
- `status` VARCHAR(20) - 运行状态（正常/故障/维修中等）
- `description` TEXT - 设备描述
- `location` VARCHAR(100) - 设备位置
- `created_at` TIMESTAMP - 创建时间
- `updated_at` TIMESTAMP - 更新时间

### 设备实时状态表（equipment_status）

- `id` INT - 主键
- `equipment_id` INT - 设备ID（外键关联equipment表）
- `runtime_hours` FLOAT - 运行时长（小时）
- `collection_time` TIMESTAMP - 数据采集时间
- `sensor_data` JSON - 传感器实时数据（存储所有传感器数据，如温度、压力、振动、速度等）
- `fault_probability` FLOAT - 估计故障概率

## 使用方法

### 创建设备相关表

```bash
python equipment_manager.py create-tables
```

### 添加新设备

```bash
python equipment_manager.py add-equipment --data '{"equipment_name": "注塑机A-01", "equipment_code": "JSJ-A01", "line_id": "1", "equipment_type": "注塑机", "status": "正常", "description": "用于生产塑料外壳的注塑设备", "location": "车间A区"}'
```

### 更新设备状态

```bash
python equipment_manager.py update-status --equipment-id 1 --data '{"runtime_hours": 126.5, "sensor_data": {"temperature": 85.2, "pressure": 18.5, "vibration": 0.05, "speed": 850}, "fault_probability": 0.15}'
```

### 获取设备列表

获取所有设备：
```bash
python equipment_manager.py list
```

按产线筛选：
```bash
python equipment_manager.py list --line-id 1
```

按状态筛选：
```bash
python equipment_manager.py list --status "正常"
```

### 获取设备状态

获取最新状态：
```bash
python equipment_manager.py get-status --equipment-id 1
```

获取多条状态记录：
```bash
python equipment_manager.py get-status --equipment-id 1 --limit 5
```

### 获取设备及其最新状态

获取所有设备及其状态：
```bash
python equipment_manager.py get-with-status
```

按产线获取设备及其状态：
```bash
python equipment_manager.py get-with-status --line-id 1
```

## 注意事项

1. 请确保已安装所需的Python依赖：
   ```bash
   pip install mysql-connector-python
   ```

2. 请根据实际情况修改数据库连接信息（host, user, password）。

3. 所有命令的输出均为JSON格式，便于与前端交互。

4. `sensor_data`字段使用JSON格式存储，可以灵活存储不同类型的传感器数据，如温度、压力、振动、速度等。所有传感器数据都存储在这个字段中，而不是单独的列。

5. 设备状态表与设备表通过`equipment_id`外键关联，删除设备时会级联删除相关的状态记录。
