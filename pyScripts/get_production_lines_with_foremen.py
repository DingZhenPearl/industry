#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
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

# 数据库连接函数
def get_db_connection():
    """创建并返回数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',  # 请根据实际情况修改密码
            database='industry_db'
        )
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

def get_production_lines_with_foremen():
    """获取产线信息及其负责的工长信息"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查询产线信息及其最新状态
        query = """
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
        """
        
        cursor.execute(query)
        production_lines = cursor.fetchall()

        # 处理JSON字段
        for line in production_lines:
            if 'equipment_list' in line and line['equipment_list']:
                try:
                    if isinstance(line['equipment_list'], str):
                        line['equipment_list'] = json.loads(line['equipment_list'])
                except:
                    pass  # 如果解析失败，保持原样

        # 查询所有工长信息
        query = """
            SELECT 
                employee_id as id,
                username as name,
                phone,
                group_id,
                line_id,
                COALESCE(status, 'active') as status,
                CASE
                    WHEN status = 'leave' THEN '请假'
                    WHEN status = 'off' THEN '离岗'
                    ELSE '在岗'
                END as statusText
            FROM users
            WHERE role = 'foreman'
        """
        
        cursor.execute(query)
        foremen = cursor.fetchall()

        # 将工长信息添加到产线数据中
        for line in production_lines:
            line['foremen'] = []
            line_id_str = str(line['id'])
            
            for foreman in foremen:
                if foreman['line_id'] == line_id_str:
                    line['foremen'].append(foreman)

        print(json.dumps({
            'success': True,
            'data': production_lines
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取产线及工长信息时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    get_production_lines_with_foremen()
