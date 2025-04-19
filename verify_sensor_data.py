#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error

# 连接数据库
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='mwYgR7#*X2',
        database='industry_db'
    )
    
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        
        # 查询包装机H-01的传感器项目列表
        query = "SELECT id, equipment_name, sensor_projects FROM equipment WHERE id = 6"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            print(f"设备ID: {result['id']}")
            print(f"设备名称: {result['equipment_name']}")
            
            if result['sensor_projects']:
                sensor_projects = json.loads(result['sensor_projects'])
                print("传感器项目列表:")
                for key, value in sensor_projects.items():
                    print(f"  - {key}: {value}")
            else:
                print("传感器项目列表为空")
        else:
            print("未找到包装机H-01")
        
except Error as e:
    print(f"数据库错误: {e}")
    
finally:
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("数据库连接已关闭")
