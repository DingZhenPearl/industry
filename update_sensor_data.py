#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error

# 读取JSON文件
with open('sensor_data.json', 'r', encoding='utf-8') as file:
    sensor_data = json.load(file)

# 连接数据库
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='mwYgR7#*X2',
        database='industry_db'
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        # 将JSON数据转换为字符串
        sensor_data_json = json.dumps(sensor_data, ensure_ascii=False)
        
        # 更新设备的sensor_projects字段
        query = "UPDATE equipment SET sensor_projects = %s WHERE id = %s"
        cursor.execute(query, (sensor_data_json, 6))  # 6是包装机H-01的ID
        
        connection.commit()
        print(f"成功更新包装机H-01的传感器项目列表")
        
except Error as e:
    print(f"数据库错误: {e}")
    
finally:
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("数据库连接已关闭")
