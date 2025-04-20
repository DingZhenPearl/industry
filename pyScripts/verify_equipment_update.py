#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',
            database='industry_db'
        )
        return connection
    except Error as e:
        print(f'数据库连接错误: {str(e)}')
        return None

def verify_equipment_update():
    """验证设备信息更新，特别是传感器项目字段"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 查询设备信息
        query = "SELECT id, equipment_name, equipment_code, sensor_projects FROM equipment WHERE id = 6"
        cursor.execute(query)
        equipment = cursor.fetchone()
        
        if not equipment:
            print("未找到ID为6的设备")
            return
        
        print(f"设备ID: {equipment['id']}")
        print(f"设备名称: {equipment['equipment_name']}")
        print(f"设备编码: {equipment['equipment_code']}")
        
        # 处理传感器项目字段
        if equipment['sensor_projects']:
            if isinstance(equipment['sensor_projects'], str):
                sensor_projects = json.loads(equipment['sensor_projects'])
            else:
                sensor_projects = equipment['sensor_projects']
                
            print("传感器项目:")
            for key, value in sensor_projects.items():
                print(f"  - {key}: {value}")
        else:
            print("传感器项目为空")
            
    except Error as e:
        print(f"查询设备信息时出错: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verify_equipment_update()
