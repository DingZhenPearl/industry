#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import time

# 创建产线表
def create_tables():
    print("创建产线表...")
    result = subprocess.run(
        ["python", "pyScripts/production_line_manager.py", "create-tables", "--drop"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(result.stdout)
    return "success" in result.stdout

# 添加示例产线
def add_sample_production_lines():
    print("添加示例产线...")

    # 获取设备列表
    result = subprocess.run(
        ["python", "pyScripts/equipment_manager.py", "list"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    equipment_data = {}
    try:
        response = json.loads(result.stdout)
        if response.get("success") and "data" in response:
            for equipment in response["data"]:
                line_id = equipment["line_id"]
                if line_id not in equipment_data:
                    equipment_data[line_id] = []
                equipment_data[line_id].append({
                    "id": equipment["id"],
                    "name": equipment["equipment_name"],
                    "code": equipment["equipment_code"]
                })
    except:
        print(f"解析设备数据失败: {result.stdout}")
        equipment_data = {
            "1": [{"id": 1, "name": "注塑机A-01", "code": "JSJ-A01"},
                  {"id": 2, "name": "压铸机B-02", "code": "YZJ-B02"},
                  {"id": 3, "name": "检测仪C-01", "code": "JCY-C01"}],
            "2": [{"id": 4, "name": "车床D-01", "code": "CD-D01"},
                  {"id": 5, "name": "铣床E-01", "code": "XC-E01"},
                  {"id": 6, "name": "钻床F-01", "code": "ZC-F01"}],
            "3": [{"id": 7, "name": "装配线G-01", "code": "ZPX-G01"},
                  {"id": 8, "name": "包装机H-01", "code": "BZJ-H01"},
                  {"id": 9, "name": "喷涂机I-01", "code": "PTJ-I01"}]
        }

    # 产线数据
    production_lines = [
        {
            "line_name": "一号生产线",
            "equipment_list": equipment_data.get("1", []),
            "theoretical_capacity": 1000,
            "status": "正常"
        },
        {
            "line_name": "二号生产线",
            "equipment_list": equipment_data.get("2", []),
            "theoretical_capacity": 800,
            "status": "维修中"
        },
        {
            "line_name": "三号生产线",
            "equipment_list": equipment_data.get("3", []),
            "theoretical_capacity": 1200,
            "status": "正常"
        }
    ]

    line_ids = []

    for line in production_lines:
        result = subprocess.run(
            ["python", "pyScripts/production_line_manager.py", "add-line", "--data", json.dumps(line, ensure_ascii=False)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"添加产线 {line['line_name']}: {result.stdout}")

        try:
            response = json.loads(result.stdout)
            if response.get("success") and "line_id" in response:
                line_ids.append((response["line_id"], line["theoretical_capacity"]))
        except:
            print(f"解析响应失败: {result.stdout}")

    return line_ids

# 添加示例产线状态数据
def add_sample_status_data(line_ids):
    print("添加示例产线状态数据...")

    for line_id, theoretical_capacity in line_ids:
        # 生成随机运行时长
        runtime_hours = 100 + (line_id * 12.5)

        # 生成实时产能（理论产能的80%-95%之间）
        real_time_capacity = theoretical_capacity * (0.8 + (line_id * 0.05))

        status_data = {
            "runtime_hours": runtime_hours,
            "real_time_capacity": real_time_capacity
        }

        result = subprocess.run(
            ["python", "pyScripts/production_line_manager.py", "update-status",
             "--line-id", str(line_id),
             "--data", json.dumps(status_data, ensure_ascii=False)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"添加产线ID {line_id} 的状态数据: {result.stdout}")

        # 添加一些历史数据点
        for i in range(1, 4):
            # 稍微变化一下数据
            modified_data = {
                "runtime_hours": runtime_hours - (i * 8),  # 每8小时一个数据点
                "real_time_capacity": real_time_capacity * (0.95 + (i * 0.01))  # 稍微变化产能
            }

            # 添加延迟，确保时间戳不同
            time.sleep(1)

            result = subprocess.run(
                ["python", "pyScripts/production_line_manager.py", "update-status",
                 "--line-id", str(line_id),
                 "--data", json.dumps(modified_data, ensure_ascii=False)],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            print(f"添加产线ID {line_id} 的历史数据点 {i}: {result.stdout}")

def main():
    print("初始化产线数据...")

    # 创建表
    if not create_tables():
        print("创建表失败，退出初始化")
        return

    # 添加示例产线
    line_ids = add_sample_production_lines()
    if not line_ids:
        print("添加示例产线失败，退出初始化")
        return

    # 添加示例状态数据
    add_sample_status_data(line_ids)

    print("产线数据初始化完成！")

if __name__ == "__main__":
    main()
