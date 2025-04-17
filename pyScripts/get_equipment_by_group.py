#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import sys
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 自定义JSON编码器，处理日期时间类型
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DateTimeEncoder, self).default(obj)

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',  # 请根据实际情况修改密码
            database='industry_db'
        )
        return connection
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'数据库连接失败: {str(e)}'
        }, ensure_ascii=False))
        exit(1)

def get_equipment_by_group(group_id):
    """获取指定组号对应的设备列表及其最新状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查询该组号对应的工长
        query_foremen = """
            SELECT employee_id
            FROM users
            WHERE group_id = %s AND role = 'foreman'
        """
        cursor.execute(query_foremen, (group_id,))
        foremen = cursor.fetchall()

        if not foremen:
            # 如果没有找到工长，返回空列表
            print(json.dumps({
                'success': True,
                'data': []
            }, ensure_ascii=False))
            return

        # 提取工长工号列表
        foreman_ids = [foreman['employee_id'] for foreman in foremen]

        # 构建IN子句的参数占位符
        placeholders = ', '.join(['%s'] * len(foreman_ids))

        # 查询这些工长负责的产线ID
        query_lines = f"""
            SELECT id
            FROM production_line
            WHERE foreman_id IN ({placeholders})
        """

        cursor.execute(query_lines, foreman_ids)
        lines = cursor.fetchall()

        if not lines:
            # 如果没有找到产线，返回空列表
            print(json.dumps({
                'success': True,
                'data': []
            }, ensure_ascii=False))
            return

        # 提取产线ID列表
        line_ids = [line['id'] for line in lines]

        # 构建IN子句的参数占位符
        line_placeholders = ', '.join(['%s'] * len(line_ids))

        # 查询这些产线上的设备及其最新状态，并关联查询产线名称
        query = f"""
            SELECT e.*,
                   es.runtime_hours,
                   es.collection_time,
                   es.sensor_data,
                   es.fault_probability,
                   pl.line_name
            FROM equipment e
            LEFT JOIN (
                SELECT es1.*
                FROM equipment_status es1
                INNER JOIN (
                    SELECT equipment_id, MAX(collection_time) as max_time
                    FROM equipment_status
                    GROUP BY equipment_id
                ) es2 ON es1.equipment_id = es2.equipment_id AND es1.collection_time = es2.max_time
            ) es ON e.id = es.equipment_id
            LEFT JOIN production_line pl ON e.line_id = pl.id
            WHERE e.line_id IN ({line_placeholders})
        """

        cursor.execute(query, line_ids)
        equipment_data = cursor.fetchall()

        # 处理JSON字段
        for equipment in equipment_data:
            if 'sensor_data' in equipment and equipment['sensor_data']:
                try:
                    if isinstance(equipment['sensor_data'], str):
                        equipment['sensor_data'] = json.loads(equipment['sensor_data'])
                except:
                    pass  # 如果解析失败，保持原样

        print(json.dumps({
            'success': True,
            'data': equipment_data
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取组号对应设备时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    parser = argparse.ArgumentParser(description='获取指定组号对应的设备列表')
    parser.add_argument('group_id', help='组号')

    args = parser.parse_args()
    get_equipment_by_group(args.group_id)

if __name__ == "__main__":
    main()
