# 设备传感器项目管理

本文档介绍如何使用新添加的`sensor_projects`字段来管理设备的传感器项目列表。

## 字段说明

`sensor_projects`字段是一个JSON类型的字段，用于存储设备的传感器项目列表。它不存储具体的传感器数据，而是存储传感器项目的名称和配置信息。

## 数据格式示例

```json
{
  "temperature": {
    "name": "温度",
    "unit": "°C",
    "warning_threshold": 85,
    "error_threshold": 95
  },
  "pressure": {
    "name": "压力",
    "unit": "MPa",
    "warning_threshold": 18,
    "error_threshold": 20
  },
  "vibration": {
    "name": "振动",
    "unit": "mm/s",
    "warning_threshold": 0.1,
    "error_threshold": 0.2
  },
  "speed": {
    "name": "转速",
    "unit": "rpm",
    "warning_threshold": 900,
    "error_threshold": 950
  }
}
```

## 使用方法

### 更新设备传感器项目列表

```bash
python update_equipment_sensor_projects.py update --equipment-id 1 --data '{"temperature": {"name": "温度", "unit": "°C", "warning_threshold": 85, "error_threshold": 95}, "pressure": {"name": "压力", "unit": "MPa", "warning_threshold": 18, "error_threshold": 20}}'
```

### 获取设备传感器项目列表

```bash
python update_equipment_sensor_projects.py get --equipment-id 1
```

## API接口

### 获取设备传感器项目列表

```
GET /api/sensor-projects/:equipment_id
```

### 更新设备传感器项目列表

```
POST /api/sensor-projects/:equipment_id
```

请求体示例：
```json
{
  "temperature": {
    "name": "温度",
    "unit": "°C",
    "warning_threshold": 85,
    "error_threshold": 95
  },
  "pressure": {
    "name": "压力",
    "unit": "MPa",
    "warning_threshold": 18,
    "error_threshold": 20
  }
}
```

## 与设备状态表的关系

`equipment`表中的`sensor_projects`字段定义了设备支持的传感器项目列表，而`equipment_status`表中的`sensor_data`字段存储了这些传感器的实时数据。

例如，如果`sensor_projects`字段包含了"temperature"和"pressure"两个项目，那么`sensor_data`字段中应该包含这两个项目的实时数据：

```json
{
  "temperature": 78.5,
  "pressure": 16.2
}
```

这种设计使得系统能够灵活地支持不同类型的设备和传感器，同时保持数据的一致性和可维护性。
