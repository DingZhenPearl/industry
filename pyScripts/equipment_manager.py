#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import mysql.connector
from mysql.connector import Error
import io
import argparse
from datetime import datetime

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# =============================================
# 数据库连接函数
# =============================================
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

# =============================================
# 日期时间JSON编码器
# =============================================
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DateTimeEncoder, self).default(obj)

# =============================================
# 设备表操作函数
# =============================================
def create_equipment_tables(drop_existing=False):
    """创建设备静态信息表和设备状态表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 如果需要，先删除现有表
        if drop_existing:
            cursor.execute("DROP TABLE IF EXISTS equipment_status")
            cursor.execute("DROP TABLE IF EXISTS equipment")
            print("\u5df2删除现有表")

        # 创建设备静态信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                equipment_name VARCHAR(100) NOT NULL COMMENT '设备名称',
                equipment_code VARCHAR(50) NOT NULL UNIQUE COMMENT '设备编码',
                line_id VARCHAR(50) NOT NULL COMMENT '所属产线ID',
                equipment_type VARCHAR(50) COMMENT '设备类型',
                status VARCHAR(20) DEFAULT '正常' COMMENT '运行状态',
                worker_id VARCHAR(20) NULL COMMENT '负责工人的工号',
                description TEXT COMMENT '设备描述',
                location VARCHAR(100) COMMENT '设备位置',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_line_id (line_id),
                INDEX idx_status (status),
                INDEX idx_worker_id (worker_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备静态信息表'
        """)

        # 创建设备状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                equipment_id INT NOT NULL COMMENT '设备ID',
                runtime_hours FLOAT DEFAULT 0 COMMENT '运行时长(小时)',
                collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
                sensor_data JSON COMMENT '传感器实时数据',
                fault_probability FLOAT DEFAULT 0 COMMENT '估计故障概率',
                FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
                INDEX idx_equipment_id (equipment_id),
                INDEX idx_collection_time (collection_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备实时状态表'
        """)

        connection.commit()
        print(json.dumps({
            'success': True,
            'message': '设备表创建成功'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'创建设备表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def add_equipment(equipment_data):
    """添加新设备"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 构建插入语句
        fields = []
        placeholders = []
        values = []

        for key, value in equipment_data.items():
            if key not in ['id', 'created_at', 'updated_at']:  # 跳过自动生成的字段
                fields.append(key)
                placeholders.append('%s')
                values.append(value)

        query = f"""
            INSERT INTO equipment ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        equipment_id = cursor.lastrowid
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '设备添加成功',
            'equipment_id': equipment_id
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'添加设备时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_equipment_status(equipment_id, status_data):
    """更新设备状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 如果包含传感器数据，转换为JSON字符串
        if 'sensor_data' in status_data and isinstance(status_data['sensor_data'], dict):
            status_data['sensor_data'] = json.dumps(status_data['sensor_data'])

        # 构建插入语句
        fields = ['equipment_id']
        placeholders = ['%s']
        values = [equipment_id]

        for key, value in status_data.items():
            if key not in ['id', 'equipment_id', 'collection_time']:  # 跳过自动生成的字段
                fields.append(key)
                placeholders.append('%s')
                values.append(value)

        query = f"""
            INSERT INTO equipment_status ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        status_id = cursor.lastrowid
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '设备状态更新成功',
            'status_id': status_id
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'更新设备状态时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def assign_worker_to_equipment(equipment_id, worker_id):
    """分配工人到设备"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 更新设备的负责工人
        query = "UPDATE equipment SET worker_id = %s WHERE id = %s"
        cursor.execute(query, (worker_id, equipment_id))
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': f'已成功将工人 {worker_id} 分配给设备 {equipment_id}'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'分配工人到设备时出错: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_equipment_list(line_id=None, status=None):
    """获取设备列表，可按产线和状态筛选"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM equipment WHERE 1=1"
        params = []

        if line_id:
            query += " AND line_id = %s"
            params.append(line_id)

        if status:
            query += " AND status = %s"
            params.append(status)

        cursor.execute(query, params)
        equipment_list = cursor.fetchall()

        print(json.dumps({
            'success': True,
            'data': equipment_list
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取设备列表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_equipment_status(equipment_id, limit=1):
    """获取设备最新状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM equipment_status
            WHERE equipment_id = %s
            ORDER BY collection_time DESC
            LIMIT %s
        """

        cursor.execute(query, (equipment_id, limit))
        status_data = cursor.fetchall()

        # 处理JSON字段
        for item in status_data:
            if 'sensor_data' in item and item['sensor_data']:
                try:
                    if isinstance(item['sensor_data'], str):
                        item['sensor_data'] = json.loads(item['sensor_data'])
                except:
                    pass  # 如果解析失败，保持原样

        print(json.dumps({
            'success': True,
            'data': status_data
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取设备状态时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_equipment_with_status(line_id=None, equipment_id=None):
    """获取设备信息及其最新状态，并关联查询产线名称"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
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
        """

        params = []
        where_clauses = []

        if line_id:
            where_clauses.append("e.line_id = %s")
            params.append(line_id)

        if equipment_id:
            where_clauses.append("e.id = %s")
            params.append(equipment_id)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
        equipment_data = cursor.fetchall()

        # 处理JSON字段
        for item in equipment_data:
            if 'sensor_data' in item and item['sensor_data']:
                try:
                    if isinstance(item['sensor_data'], str):
                        item['sensor_data'] = json.loads(item['sensor_data'])
                except:
                    pass  # 如果解析失败，保持原样

        print(json.dumps({
            'success': True,
            'data': equipment_data
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取设备及状态时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 主函数
# =============================================
def main():
    parser = argparse.ArgumentParser(description='设备管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 创建表命令
    create_parser = subparsers.add_parser('create-tables', help='创建设备相关表')
    create_parser.add_argument('--drop', action='store_true', help='删除现有表后重新创建')

    # 添加设备命令
    add_parser = subparsers.add_parser('add-equipment', help='添加新设备')
    add_parser.add_argument('--data', required=True, help='设备数据(JSON格式)')

    # 更新设备状态命令
    update_parser = subparsers.add_parser('update-status', help='更新设备状态')
    update_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')
    update_parser.add_argument('--data', required=True, help='状态数据(JSON格式)')

    # 分配工人到设备命令
    assign_worker_parser = subparsers.add_parser('assign-worker', help='分配工人到设备')
    assign_worker_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')
    assign_worker_parser.add_argument('--worker-id', required=True, help='工人工号')

    # 获取设备列表命令
    list_parser = subparsers.add_parser('list', help='获取设备列表')
    list_parser.add_argument('--line-id', help='按产线ID筛选')
    list_parser.add_argument('--status', help='按状态筛选')

    # 获取设备状态命令
    status_parser = subparsers.add_parser('get-status', help='获取设备状态')
    status_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')
    status_parser.add_argument('--limit', type=int, default=1, help='返回记录数量')

    # 获取设备及其状态命令
    combined_parser = subparsers.add_parser('get-with-status', help='获取设备及其最新状态')
    combined_parser.add_argument('--line-id', help='按产线ID筛选')
    combined_parser.add_argument('--equipment-id', type=int, help='按设备ID筛选')

    args = parser.parse_args()

    if args.command == 'create-tables':
        create_equipment_tables(drop_existing=args.drop)
    elif args.command == 'add-equipment':
        try:
            equipment_data = json.loads(args.data)
            add_equipment(equipment_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'update-status':
        try:
            status_data = json.loads(args.data)
            update_equipment_status(args.equipment_id, status_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'assign-worker':
        assign_worker_to_equipment(args.equipment_id, args.worker_id)
    elif args.command == 'list':
        get_equipment_list(args.line_id, args.status)
    elif args.command == 'get-status':
        get_equipment_status(args.equipment_id, args.limit)
    elif args.command == 'get-with-status':
        get_equipment_with_status(args.line_id, args.equipment_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
