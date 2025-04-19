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

def add_sensor_projects_field():
    """为equipment表添加sensor_projects字段"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'industry_db'
            AND TABLE_NAME = 'equipment'
            AND COLUMN_NAME = 'sensor_projects'
        """)

        if cursor.fetchone()[0] > 0:
            print(json.dumps({
                'success': False,
                'message': 'sensor_projects字段已存在'
            }, ensure_ascii=False))
            return

        # 添加sensor_projects字段
        cursor.execute("""
            ALTER TABLE equipment
            ADD COLUMN sensor_projects JSON COMMENT '传感器项目列表'
        """)

        connection.commit()
        print(json.dumps({
            'success': True,
            'message': '成功添加sensor_projects字段到equipment表'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'添加字段时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_sensor_projects_field()
