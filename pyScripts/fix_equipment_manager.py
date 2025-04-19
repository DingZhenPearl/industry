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

def fix_add_equipment_function():
    """修复equipment_manager.py中的add_equipment函数，添加对JSON字段的处理"""
    try:
        # 读取原始文件
        with open('pyScripts/equipment_manager.py', 'r', encoding='utf-8') as file:
            content = file.read()

        # 查找add_equipment函数中的构建插入语句部分
        start_marker = "def add_equipment(equipment_data):"
        end_marker = "    except Error as e:"
        
        start_index = content.find(start_marker)
        end_index = content.find(end_marker, start_index)
        
        if start_index == -1 or end_index == -1:
            print(json.dumps({
                'success': False,
                'error': '无法在文件中找到add_equipment函数'
            }, ensure_ascii=False))
            return

        # 提取原始函数内容
        original_function = content[start_index:end_index]
        
        # 修改函数，添加对JSON字段的处理
        new_function = original_function.replace(
            "        # 构建插入语句\n        fields = []\n        placeholders = []\n        values = []",
            """        # 处理JSON字段
        if 'sensor_projects' in equipment_data and isinstance(equipment_data['sensor_projects'], dict):
            equipment_data['sensor_projects'] = json.dumps(equipment_data['sensor_projects'], ensure_ascii=False)
            
        # 构建插入语句
        fields = []
        placeholders = []
        values = []"""
        )
        
        # 更新文件内容
        new_content = content.replace(original_function, new_function)
        
        # 写回文件
        with open('pyScripts/equipment_manager.py', 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        print(json.dumps({
            'success': True,
            'message': '成功修复equipment_manager.py中的add_equipment函数'
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'修复脚本时出错: {str(e)}'
        }, ensure_ascii=False))

if __name__ == "__main__":
    fix_add_equipment_function()
