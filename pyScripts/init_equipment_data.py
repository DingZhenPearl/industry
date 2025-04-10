#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import subprocess
import time
import os

# 创建设备表
def create_tables():
    print("创建设备表...")
    result = subprocess.run(
        ["python", "pyScripts/equipment_manager.py", "create-tables", "--drop"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(result.stdout)
    return "success" in result.stdout

# 添加示例设备
def add_sample_equipment():
    print("添加示例设备...")

    # 产线1的设备
    equipment_data = [
        {
            "equipment_name": "注塑机A-01",
            "equipment_code": "JSJ-A01",
            "line_id": "1",
            "equipment_type": "注塑机",
            "status": "正常",
            "description": "用于生产塑料外壳的注塑设备",
            "location": "车间A区"
        },
        {
            "equipment_name": "压铸机B-02",
            "equipment_code": "YZJ-B02",
            "line_id": "1",
            "equipment_type": "压铸机",
            "status": "正常",
            "description": "用于生产金属零件的压铸设备",
            "location": "车间A区"
        },
        {
            "equipment_name": "检测仪C-01",
            "equipment_code": "JCY-C01",
            "line_id": "1",
            "equipment_type": "检测设备",
            "status": "正常",
            "description": "用于检测产品质量的设备",
            "location": "车间A区"
        },
        # 产线2的设备
        {
            "equipment_name": "车床D-01",
            "equipment_code": "CD-D01",
            "line_id": "2",
            "equipment_type": "车床",
            "status": "正常",
            "description": "用于加工金属零件的车床",
            "location": "车间B区"
        },
        {
            "equipment_name": "铣床E-01",
            "equipment_code": "XC-E01",
            "line_id": "2",
            "equipment_type": "铣床",
            "status": "维修中",
            "description": "用于加工金属零件的铣床",
            "location": "车间B区"
        },
        {
            "equipment_name": "钻床F-01",
            "equipment_code": "ZC-F01",
            "line_id": "2",
            "equipment_type": "钻床",
            "status": "正常",
            "description": "用于钻孔的设备",
            "location": "车间B区"
        },
        # 产线3的设备
        {
            "equipment_name": "装配线G-01",
            "equipment_code": "ZPX-G01",
            "line_id": "3",
            "equipment_type": "装配线",
            "status": "正常",
            "description": "用于产品装配的生产线",
            "location": "车间C区"
        },
        {
            "equipment_name": "包装机H-01",
            "equipment_code": "BZJ-H01",
            "line_id": "3",
            "equipment_type": "包装机",
            "status": "故障",
            "description": "用于产品包装的设备",
            "location": "车间C区"
        },
        {
            "equipment_name": "喷涂机I-01",
            "equipment_code": "PTJ-I01",
            "line_id": "3",
            "equipment_type": "喷涂机",
            "status": "正常",
            "description": "用于产品表面处理的设备",
            "location": "车间C区"
        }
    ]

    equipment_ids = []

    for equipment in equipment_data:
        result = subprocess.run(
            ["python", "pyScripts/equipment_manager.py", "add-equipment", "--data", json.dumps(equipment, ensure_ascii=False)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"添加设备 {equipment['equipment_name']}: {result.stdout}")

        try:
            response = json.loads(result.stdout)
            if response.get("success") and "equipment_id" in response:
                equipment_ids.append((response["equipment_id"], equipment["equipment_type"]))
        except:
            print(f"解析响应失败: {result.stdout}")

    return equipment_ids

# 添加示例设备状态数据
def add_sample_status_data(equipment_ids):
    print("添加示例设备状态数据...")

    for equipment_id, equipment_type in equipment_ids:
        # 根据设备类型生成不同的传感器数据
        if "注塑机" in equipment_type:
            sensor_data = {
                "temperature": 85.2,
                "pressure": 18.5,
                "vibration": 0.05,
                "speed": 850
            }
            fault_probability = 0.15
            temperature = 85.2
            pressure = 18.5
            vibration = 0.05
            speed = 850
        elif "压铸机" in equipment_type:
            sensor_data = {
                "temperature": 95.7,
                "pressure": 22.3,
                "vibration": 0.08,
                "speed": 650
            }
            fault_probability = 0.25
            temperature = 95.7
            pressure = 22.3
            vibration = 0.08
            speed = 650
        elif "检测" in equipment_type:
            sensor_data = {
                "temperature": 35.1,
                "vibration": 0.02,
                "speed": 120
            }
            fault_probability = 0.05
            temperature = 35.1
            pressure = None
            vibration = 0.02
            speed = 120
        elif "车床" in equipment_type or "铣床" in equipment_type or "钻床" in equipment_type:
            sensor_data = {
                "temperature": 65.3,
                "vibration": 0.12,
                "speed": 1200
            }
            fault_probability = 0.18
            temperature = 65.3
            pressure = None
            vibration = 0.12
            speed = 1200
        elif "装配线" in equipment_type:
            sensor_data = {
                "temperature": 28.5,
                "vibration": 0.03,
                "speed": 60
            }
            fault_probability = 0.08
            temperature = 28.5
            pressure = None
            vibration = 0.03
            speed = 60
        elif "包装机" in equipment_type:
            sensor_data = {
                "temperature": 32.1,
                "pressure": 5.2,
                "vibration": 0.07,
                "speed": 90
            }
            fault_probability = 0.35  # 故障概率较高
            temperature = 32.1
            pressure = 5.2
            vibration = 0.07
            speed = 90
        elif "喷涂机" in equipment_type:
            sensor_data = {
                "temperature": 42.8,
                "pressure": 8.5,
                "vibration": 0.04,
                "speed": 180
            }
            fault_probability = 0.12
            temperature = 42.8
            pressure = 8.5
            vibration = 0.04
            speed = 180
        else:
            sensor_data = {
                "temperature": 30.0,
                "vibration": 0.05,
                "speed": 100
            }
            fault_probability = 0.10
            temperature = 30.0
            pressure = None
            vibration = 0.05
            speed = 100

        # 生成随机运行时长
        runtime_hours = 100 + (equipment_id * 10.5)

        status_data = {
            "runtime_hours": runtime_hours,
            "sensor_data": sensor_data,
            "fault_probability": fault_probability
        }

        result = subprocess.run(
            ["python", "pyScripts/equipment_manager.py", "update-status",
             "--equipment-id", str(equipment_id),
             "--data", json.dumps(status_data, ensure_ascii=False)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"添加设备ID {equipment_id} 的状态数据: {result.stdout}")

        # 添加一些历史数据点
        for i in range(1, 4):
            # 稍微变化一下数据
            modified_data = status_data.copy()
            modified_data["runtime_hours"] = runtime_hours - (i * 8)  # 每8小时一个数据点

            # 修改传感器数据
            modified_sensor_data = sensor_data.copy()
            for key in modified_sensor_data:
                if isinstance(modified_sensor_data[key], (int, float)):
                    # 添加一些随机变化
                    modified_sensor_data[key] = round(modified_sensor_data[key] * (0.95 + (i * 0.02)), 2)

            modified_data["sensor_data"] = modified_sensor_data

            # 传感器数据已包含在sensor_data字段中

            # 调整故障概率
            modified_data["fault_probability"] = round(fault_probability * (0.9 + (i * 0.05)), 2)

            # 添加延迟，确保时间戳不同
            time.sleep(1)

            result = subprocess.run(
                ["python", "pyScripts/equipment_manager.py", "update-status",
                 "--equipment-id", str(equipment_id),
                 "--data", json.dumps(modified_data, ensure_ascii=False)],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print(f"添加设备ID {equipment_id} 的历史数据点 {i}: {result.stdout}")

def main():
    print("初始化设备数据...")

    # 创建表
    if not create_tables():
        print("创建表失败，退出初始化")
        return

    # 添加示例设备
    equipment_ids = add_sample_equipment()
    if not equipment_ids:
        print("添加示例设备失败，退出初始化")
        return

    # 添加示例状态数据
    add_sample_status_data(equipment_ids)

    print("设备数据初始化完成！")

if __name__ == "__main__":
    main()
