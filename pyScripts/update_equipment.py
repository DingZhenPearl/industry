#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import json
import mysql.connector
from mysql.connector import Error
import io
from datetime import datetime

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 日期时间JSON编码器
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DateTimeEncoder, self).default(obj)

# 获取数据库连接
def get_db_connection():
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
        return None

# 更新设备静态信息
def update_equipment(equipment_id, equipment_data):
    """更新设备静态信息，包括状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 处理JSON字段
        if 'sensor_projects' in equipment_data and isinstance(equipment_data['sensor_projects'], dict):
            equipment_data['sensor_projects'] = json.dumps(equipment_data['sensor_projects'], ensure_ascii=False)

        # 构建更新语句
        set_clauses = []
        values = []

        for key, value in equipment_data.items():
            if key not in ['id', 'created_at', 'updated_at']:  # 跳过自动生成的字段
                set_clauses.append(f"{key} = %s")
                values.append(value)

        # 添加equipment_id到values列表
        values.append(equipment_id)

        query = f"""
            UPDATE equipment
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """

        cursor.execute(query, values)
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '设备信息更新成功'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'更新设备信息时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    parser = argparse.ArgumentParser(description='更新设备静态信息')
    parser.add_argument('--equipment-id', required=True, help='设备ID')
    parser.add_argument('--data', required=True, help='更新的数据，JSON格式')

    args = parser.parse_args()

    try:
        equipment_data = json.loads(args.data)
        update_equipment(args.equipment_id, equipment_data)
    except json.JSONDecodeError:
        print(json.dumps({
            'success': False,
            'error': 'JSON解析错误，请检查数据格式'
        }, ensure_ascii=False))

if __name__ == '__main__':
    main()
