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

def get_production_lines_by_group(group_id):
    """获取指定组号对应的产线列表及其最新状态"""
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

        # 查询这些工长负责的产线及其最新状态
        query = f"""
            SELECT pl.*,
                   pls.runtime_hours,
                   pls.real_time_capacity,
                   pls.collection_time
            FROM production_line pl
            LEFT JOIN (
                SELECT pls1.*
                FROM production_line_status pls1
                INNER JOIN (
                    SELECT line_id, MAX(collection_time) as max_time
                    FROM production_line_status
                    GROUP BY line_id
                ) pls2 ON pls1.line_id = pls2.line_id AND pls1.collection_time = pls2.max_time
            ) pls ON pl.id = pls.line_id
            WHERE pl.foreman_id IN ({placeholders})
        """

        cursor.execute(query, foreman_ids)
        line_data = cursor.fetchall()

        # 处理JSON字段
        for line in line_data:
            if 'equipment_list' in line and line['equipment_list']:
                try:
                    if isinstance(line['equipment_list'], str):
                        line['equipment_list'] = json.loads(line['equipment_list'])
                except:
                    pass  # 如果解析失败，保持原样

        print(json.dumps({
            'success': True,
            'data': line_data
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取组号对应产线时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    parser = argparse.ArgumentParser(description='获取指定组号对应的产线列表')
    parser.add_argument('group_id', help='组号')

    args = parser.parse_args()
    get_production_lines_by_group(args.group_id)

if __name__ == "__main__":
    main()
