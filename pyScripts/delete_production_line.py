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

def delete_production_line(line_id):
    """删除产线"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 首先检查产线是否存在
        cursor.execute("SELECT id, line_name FROM production_line WHERE id = %s", (line_id,))
        line = cursor.fetchone()

        if not line:
            print(json.dumps({
                'success': False,
                'error': f'未找到ID为{line_id}的产线'
            }, ensure_ascii=False))
            return

        line_name = line[1]

        # 检查是否有设备关联到该产线
        cursor.execute("SELECT COUNT(*) FROM equipment WHERE line_id = %s", (line_id,))
        equipment_count = cursor.fetchone()[0]

        if equipment_count > 0:
            print(json.dumps({
                'success': False,
                'error': f'产线"{line_name}"上还有{equipment_count}个设备，请先删除或转移这些设备'
            }, ensure_ascii=False))
            return

        # 删除产线状态记录
        cursor.execute("DELETE FROM production_line_status WHERE line_id = %s", (line_id,))

        # 删除产线
        cursor.execute("DELETE FROM production_line WHERE id = %s", (line_id,))
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': f'产线"{line_name}"删除成功',
            'line_id': line_id
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'删除产线时出错: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='删除产线')
    parser.add_argument('--line-id', required=True, help='产线ID')

    args = parser.parse_args()
    delete_production_line(args.line_id)
