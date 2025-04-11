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

def get_equipment_with_workers(line_id=None):
    """获取设备信息及其负责的工人信息"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 构建查询条件
        where_clause = ""
        params = []
        if line_id:
            where_clause = "WHERE e.line_id = %s"
            params.append(line_id)

        # 查询设备信息及其最新状态
        query = f"""
            SELECT e.*,
                   es.runtime_hours,
                   es.collection_time,
                   es.sensor_data,
                   es.fault_probability
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
            {where_clause}
        """

        cursor.execute(query, params)
        equipment_list = cursor.fetchall()

        # 处理JSON字段
        for equip in equipment_list:
            if 'sensor_data' in equip and equip['sensor_data']:
                try:
                    if isinstance(equip['sensor_data'], str):
                        equip['sensor_data'] = json.loads(equip['sensor_data'])
                except:
                    pass  # 如果解析失败，保持原样

        # 查询所有工人信息
        query = """
            SELECT
                id,
                employee_id,
                username as name,
                phone,
                group_id,
                COALESCE(status, 'active') as status,
                CASE
                    WHEN status = 'leave' THEN '请假'
                    WHEN status = 'off' THEN '离岗'
                    ELSE '在岗'
                END as statusText
            FROM users
            WHERE role = 'member'
        """

        cursor.execute(query)
        workers = cursor.fetchall()

        # 将工人信息添加到设备数据中
        for equip in equipment_list:
            equip['worker'] = None
            worker_id = equip['worker_id']

            if worker_id:
                for worker in workers:
                    if worker['employee_id'] == worker_id:
                        equip['worker'] = worker
                        break

        print(json.dumps({
            'success': True,
            'data': equipment_list
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取设备及工人信息时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        line_id = sys.argv[1]
        get_equipment_with_workers(line_id)
    else:
        get_equipment_with_workers()
