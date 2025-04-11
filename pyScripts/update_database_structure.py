#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import mysql.connector
from mysql.connector import Error
import io
import subprocess

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    """更新数据库结构：
    1. 从users表中删除line_id和machine_id字段
    2. 在production_line表中添加foreman_id字段
    3. 在equipment表中添加worker_id字段
    """
    print("开始更新数据库结构...")

    # 步骤1: 从users表中删除line_id和machine_id字段
    print("\n步骤1: 从users表中删除line_id和machine_id字段")
    result = subprocess.run(
        ["python", "pyScripts/user_data_operations.py", "remove-fields"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(result.stdout)

    # 步骤2: 重新创建production_line表，添加foreman_id字段
    print("\n步骤2: 更新production_line表，添加foreman_id字段")
    result = subprocess.run(
        ["python", "pyScripts/production_line_manager.py", "create-tables", "--drop"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(result.stdout)

    # 步骤3: 重新创建equipment表，添加worker_id字段
    print("\n步骤3: 更新equipment表，添加worker_id字段")
    result = subprocess.run(
        ["python", "pyScripts/equipment_manager.py", "create-tables", "--drop"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(result.stdout)

    # 步骤4: 添加一些测试数据
    print("\n步骤4: 添加测试数据")
    add_test_data()

    print("\n数据库结构更新完成！")

def add_test_data():
    """添加测试数据"""
    try:
        # 添加产线数据
        add_production_lines()

        # 添加设备数据
        add_equipment()

        # 分配工长到产线
        assign_foremen_to_lines()

        # 分配工人到设备
        assign_workers_to_equipment()

    except Exception as e:
        print(f"添加测试数据时出错: {e}")

def add_production_lines():
    """添加产线测试数据"""
    lines = [
        {
            "line_name": "一号生产线",
            "equipment_list": ["注塑机A-01", "压铸机B-02", "检测仪C-01"],
            "theoretical_capacity": 1000,
            "status": "正常"
        },
        {
            "line_name": "二号生产线",
            "equipment_list": ["车床D-01", "铣床E-01", "钻床F-01"],
            "theoretical_capacity": 800,
            "status": "正常"
        },
        {
            "line_name": "三号生产线",
            "equipment_list": ["组装台G-01", "包装机H-01", "喷漆室I-01"],
            "theoretical_capacity": 1200,
            "status": "正常"
        }
    ]

    for line in lines:
        result = subprocess.run(
            ["python", "pyScripts/production_line_manager.py", "add-line", "--data", json.dumps(line, ensure_ascii=False)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"添加产线 {line['line_name']}: {result.stdout}")

def add_equipment():
    """添加设备测试数据"""
    equipment_list = [
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
            "status": "正常",
            "description": "用于精加工的铣床",
            "location": "车间B区"
        },
        {
            "equipment_name": "组装台G-01",
            "equipment_code": "ZZT-G01",
            "line_id": "3",
            "equipment_type": "组装设备",
            "status": "正常",
            "description": "用于产品组装的工作台",
            "location": "车间C区"
        },
        {
            "equipment_name": "包装机H-01",
            "equipment_code": "BZJ-H01",
            "line_id": "3",
            "equipment_type": "包装设备",
            "status": "正常",
            "description": "用于产品包装的设备",
            "location": "车间C区"
        }
    ]

    for equip in equipment_list:
        result = subprocess.run(
            ["python", "pyScripts/equipment_manager.py", "add-equipment", "--data", json.dumps(equip, ensure_ascii=False)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"添加设备 {equip['equipment_name']}: {result.stdout}")

def assign_foremen_to_lines():
    """分配工长到产线"""
    connection = None
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',
            database='industry_db'
        )
        cursor = connection.cursor()

        # 获取工长信息
        cursor.execute("SELECT id, employee_id FROM users WHERE role = 'foreman'")
        foremen = cursor.fetchall()

        # 分配工长到产线
        for i, (foreman_id, employee_id) in enumerate(foremen, 1):
            # 确保不超过产线数量
            line_id = i
            cursor.execute(
                "UPDATE production_line SET foreman_id = %s WHERE id = %s",
                (employee_id, line_id)
            )
            print(f"分配工长ID {foreman_id}(工号:{employee_id}) 到产线ID {line_id}")

        connection.commit()
        print("工长分配完成")

    except Error as e:
        print(f"分配工长到产线时出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def assign_workers_to_equipment():
    """分配工人到设备"""
    connection = None
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',
            database='industry_db'
        )
        cursor = connection.cursor()

        # 获取工人信息
        cursor.execute("SELECT id, employee_id FROM users WHERE role = 'member'")
        workers = cursor.fetchall()

        # 获取设备信息
        cursor.execute("SELECT id FROM equipment")
        equipment = cursor.fetchall()

        # 分配工人到设备
        for i, (worker_id, employee_id) in enumerate(workers):
            # 确保不超过设备数量
            if i < len(equipment):
                equip_id = equipment[i][0]
                cursor.execute(
                    "UPDATE equipment SET worker_id = %s WHERE id = %s",
                    (employee_id, equip_id)
                )
                print(f"分配工人ID {worker_id}(工号:{employee_id}) 到设备ID {equip_id}")

        connection.commit()
        print("工人分配完成")

    except Error as e:
        print(f"分配工人到设备时出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
