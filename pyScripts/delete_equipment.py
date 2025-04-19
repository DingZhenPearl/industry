#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import argparse
import mysql.connector
from mysql.connector import Error
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

def delete_equipment(equipment_id):
    """删除设备"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 首先检查设备是否存在
        cursor.execute("SELECT id, equipment_name FROM equipment WHERE id = %s", (equipment_id,))
        equipment = cursor.fetchone()

        if not equipment:
            print(json.dumps({
                'success': False,
                'error': f'未找到ID为{equipment_id}的设备'
            }, ensure_ascii=False))
            return

        equipment_name = equipment[1]

        # 删除设备状态记录
        cursor.execute("DELETE FROM equipment_status WHERE equipment_id = %s", (equipment_id,))

        # 删除设备
        cursor.execute("DELETE FROM equipment WHERE id = %s", (equipment_id,))
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': f'设备"{equipment_name}"删除成功',
            'equipment_id': equipment_id
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'删除设备时出错: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='删除设备')
    parser.add_argument('--equipment-id', required=True, help='设备ID')

    args = parser.parse_args()
    delete_equipment(args.equipment_id)
