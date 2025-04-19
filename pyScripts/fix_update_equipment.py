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
            password='mwYgR7#*X2',
            database='industry_db'
        )
        return connection
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'数据库连接失败: {str(e)}'
        }, ensure_ascii=False))
        sys.exit(1)

def fix_update_equipment_function():
    """修复update_equipment.py中的update_equipment函数，添加对JSON字段的处理"""
    try:
        # 读取原始文件
        with open('pyScripts/update_equipment.py', 'r', encoding='utf-8') as file:
            content = file.read()

        # 查找update_equipment函数中的构建更新语句部分
        start_marker = "def update_equipment(equipment_id, equipment_data):"
        end_marker = "    except Error as e:"
        
        start_index = content.find(start_marker)
        end_index = content.find(end_marker, start_index)
        
        if start_index == -1 or end_index == -1:
            print(json.dumps({
                'success': False,
                'error': '无法在文件中找到update_equipment函数'
            }, ensure_ascii=False))
            return

        # 提取原始函数内容
        original_function = content[start_index:end_index]
        
        # 修改函数，添加对JSON字段的处理
        new_function = original_function.replace(
            "        # 构建更新语句\n        set_clauses = []\n        values = []",
            """        # 处理JSON字段
        if 'sensor_projects' in equipment_data and isinstance(equipment_data['sensor_projects'], dict):
            equipment_data['sensor_projects'] = json.dumps(equipment_data['sensor_projects'], ensure_ascii=False)
            
        # 构建更新语句
        set_clauses = []
        values = []"""
        )
        
        # 更新文件内容
        new_content = content.replace(original_function, new_function)
        
        # 写回文件
        with open('pyScripts/update_equipment.py', 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        print(json.dumps({
            'success': True,
            'message': '成功修复update_equipment.py中的update_equipment函数'
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'修复脚本时出错: {str(e)}'
        }, ensure_ascii=False))

if __name__ == "__main__":
    fix_update_equipment_function()
