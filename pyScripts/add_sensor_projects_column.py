#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error
import sys

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
            'error': f'数据库连接错误: {str(e)}'
        }, ensure_ascii=False))
        sys.exit(1)

def add_sensor_projects_column():
    """向equipment表添加sensor_projects列"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查列是否已存在
        cursor.execute("SHOW COLUMNS FROM equipment LIKE 'sensor_projects'")
        column_exists = cursor.fetchone()
        
        if column_exists:
            print(json.dumps({
                'success': True,
                'message': 'sensor_projects列已存在，无需添加'
            }, ensure_ascii=False))
            return
        
        # 添加sensor_projects列
        cursor.execute("""
            ALTER TABLE equipment
            ADD COLUMN sensor_projects JSON COMMENT '传感器项目列表'
        """)
        
        connection.commit()
        print(json.dumps({
            'success': True,
            'message': '成功添加sensor_projects列到equipment表'
        }, ensure_ascii=False))
        
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'添加列时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    add_sensor_projects_column()
