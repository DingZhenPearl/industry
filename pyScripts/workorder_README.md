# 工单管理工具使用说明

本工具用于创建和管理统一的工单信息表，支持不同类型工单的存储和查询。

## 功能列表

1. 创建工单表
2. 添加新工单
3. 更新工单信息
4. 获取单个工单详情
5. 获取工单列表（支持多种筛选条件）
6. 删除工单
7. 获取工单统计信息

## 数据表结构

工单表（workorders）包含以下字段：

### 通用字段

- `workorder_number` VARCHAR(20) - 唯一标识每个工单
- `task_type` VARCHAR(20) - 区分不同类型的工单（设备维护/产线巡检/排班任务）
- `task_details` TEXT - 问题描述或任务说明
- `start_time` DATETIME - 任务开始时间
- `deadline` DATETIME - 任务截止时间
- `actual_end_time` DATETIME - 任务实际完成时间
- `creator` VARCHAR(50) - 工单发出人
- `status` VARCHAR(20) - 工单当前状态（未接受/进行中/已完成/已取消）
- `foreman` VARCHAR(50) - 负责的工长
- `team` VARCHAR(50) - 负责的班组
- `team_members` VARCHAR(100) - 负责的具体组员
- `production_line` VARCHAR(100) - 相关产线信息
- `note` TEXT - 完成报告（工单完成人填写的报告）

### 特定字段

- `extension_fields` JSON - 存储不同工单类型的特定字段

#### 设备维护工单示例
```json
{
  "发现时间": "2024-03-19 21:26:58",
  "设备": "数控车床XX-001"
}
```

#### 排班任务工单示例
```json
{
  "设备": "数控车床XX-001"
}
```

## 使用方法

### 创建工单表

```bash
python workorder_manager.py create-table
```

### 更新工单表结构

```bash
python workorder_manager.py update-table
```

### 添加新工单

```bash
python workorder_manager.py add --data '{"task_type": "设备维护", "task_details": "设备故障需要维修", "start_time": "2024-04-10 09:00:00", "deadline": "2024-04-10 17:00:00", "creator": "admin", "foreman": "foreman1", "team": "1", "production_line": "1", "extension_fields": {"发现时间": "2024-04-10 08:30:00", "设备": "数控车床XX-001"}}'
```

### 更新工单信息

```bash
python workorder_manager.py update --number "WO20240410001" --data '{"status": "进行中", "team_members": "worker1,worker2"}'
```

### 获取单个工单详情

```bash
python workorder_manager.py get --number "WO20240410001"
```

### 获取工单列表

获取所有工单：
```bash
python workorder_manager.py list
```

按条件筛选：
```bash
python workorder_manager.py list --type "设备维护" --status "进行中" --foreman "foreman1"
```

支持的筛选条件：
- `--type`: 任务类型
- `--status`: 工单状态
- `--foreman`: 负责工长
- `--team`: 负责班组
- `--line`: 产线信息
- `--creator`: 发出人
- `--start-date`: 开始日期
- `--end-date`: 结束日期
- `--keyword`: 关键词搜索

### 删除工单

```bash
python workorder_manager.py delete --number "WO20240410001"
```

### 获取工单统计信息

```bash
python workorder_manager.py stats
```

## 注意事项

1. 工单编号会自动生成，格式为"WO" + 年月日 + 4位序号，例如：WO20240410001

2. 扩展字段使用JSON格式存储，可以根据不同工单类型存储特定的字段

3. 所有命令的输出均为JSON格式，便于与前端交互

4. 工单状态建议使用以下值：
   - 未接受
   - 进行中
   - 已完成
   - 已取消

5. 任务类型建议使用以下值：
   - 设备维护
   - 产线巡检
   - 排班任务
