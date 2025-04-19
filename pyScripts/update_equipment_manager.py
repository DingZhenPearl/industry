#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='factory'
        )
        return connection
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'数据库连接失败: {str(e)}'
        }, ensure_ascii=False))
        sys.exit(1)

def update_equipment_manager():
    """更新equipment_manager.py脚本中的create_equipment_tables函数"""
    try:
        # 读取原始文件
        with open('pyScripts/equipment_manager.py', 'r', encoding='utf-8') as file:
            content = file.read()

        # 查找create_equipment_tables函数中的equipment表创建语句
        start_marker = "CREATE TABLE IF NOT EXISTS equipment ("
        end_marker = ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备静态信息表'"
        
        start_index = content.find(start_marker)
        end_index = content.find(end_marker, start_index) + len(end_marker)
        
        if start_index == -1 or end_index == -1:
            print(json.dumps({
                'success': False,
                'error': '无法在文件中找到equipment表创建语句'
            }, ensure_ascii=False))
            return

        # 提取原始表创建语句
        original_create_table = content[start_index:end_index]
        
        # 在updated_at字段后添加sensor_projects字段
        updated_at_marker = "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',"
        sensor_projects_field = "\n                sensor_projects JSON COMMENT '传感器项目列表',"
        
        new_create_table = original_create_table.replace(
            updated_at_marker,
            updated_at_marker + sensor_projects_field
        )
        
        # 更新文件内容
        new_content = content.replace(original_create_table, new_create_table)
        
        # 写回文件
        with open('pyScripts/equipment_manager.py', 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        print(json.dumps({
            'success': True,
            'message': '成功更新equipment_manager.py脚本'
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'更新脚本时出错: {str(e)}'
        }, ensure_ascii=False))

if __name__ == "__main__":
    update_equipment_manager()
