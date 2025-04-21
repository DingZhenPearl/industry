#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error
import io
import sys
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
# 产线表操作函数
# =============================================
def create_production_line_tables(drop_existing=False):
    """创建产线静态信息表和产线状态表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 如果需要，先删除现有表
        if drop_existing:
            cursor.execute("DROP TABLE IF EXISTS production_line_status")
            cursor.execute("DROP TABLE IF EXISTS production_line")
            print("已删除现有表")

        # 创建产线静态信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_line (
                id INT AUTO_INCREMENT PRIMARY KEY,
                line_name VARCHAR(100) NOT NULL UNIQUE COMMENT '产线名称',
                equipment_list JSON COMMENT '包括的设备',
                theoretical_capacity FLOAT COMMENT '理论产能',
                status VARCHAR(20) DEFAULT '正常' COMMENT '运行状态',
                foreman_id VARCHAR(20) NULL COMMENT '负责工长工号',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_line_name (line_name),
                INDEX idx_status (status),
                INDEX idx_foreman_id (foreman_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产线静态信息表'
        """)

        # 创建产线状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production_line_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                line_id INT NOT NULL COMMENT '产线ID',
                runtime_hours FLOAT DEFAULT 0 COMMENT '运行时长(小时)',
                real_time_capacity FLOAT COMMENT '产线实时产能',
                noise_level FLOAT COMMENT '噪音水平(dB)',
                temperature FLOAT COMMENT '环境温度(°C)',
                air_quality VARCHAR(20) COMMENT '空气质量(good/medium/poor)',
                collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
                FOREIGN KEY (line_id) REFERENCES production_line(id) ON DELETE CASCADE,
                INDEX idx_line_id (line_id),
                INDEX idx_collection_time (collection_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产线实时状态表'
        """)

        connection.commit()
        print(json.dumps({
            'success': True,
            'message': '产线表创建成功'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'创建产线表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def add_production_line(line_data):
    """添加新产线"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 如果包含设备列表，转换为JSON字符串
        if 'equipment_list' in line_data and isinstance(line_data['equipment_list'], (list, dict)):
            line_data['equipment_list'] = json.dumps(line_data['equipment_list'])

        # 构建插入语句
        fields = []
        placeholders = []
        values = []

        for key, value in line_data.items():
            if key not in ['id', 'created_at', 'updated_at']:  # 跳过自动生成的字段
                fields.append(key)
                placeholders.append('%s')
                values.append(value)

        query = f"""
            INSERT INTO production_line ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        line_id = cursor.lastrowid
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '产线添加成功',
            'line_id': line_id
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'添加产线时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_production_line_status(line_id, status_data):
    """更新产线状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 构建插入语句
        fields = ['line_id']
        placeholders = ['%s']
        values = [line_id]

        for key, value in status_data.items():
            if key not in ['id', 'line_id', 'collection_time']:  # 跳过自动生成的字段
                fields.append(key)
                placeholders.append('%s')
                values.append(value)

        query = f"""
            INSERT INTO production_line_status ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        status_id = cursor.lastrowid
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '产线状态更新成功',
            'status_id': status_id
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'更新产线状态时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_production_line_list():
    """获取产线列表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM production_line"
        cursor.execute(query)
        line_list = cursor.fetchall()

        # 处理JSON字段
        for line in line_list:
            if 'equipment_list' in line and line['equipment_list']:
                try:
                    if isinstance(line['equipment_list'], str):
                        line['equipment_list'] = json.loads(line['equipment_list'])
                except:
                    pass  # 如果解析失败，保持原样

        print(json.dumps({
            'success': True,
            'data': line_list
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取产线列表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_production_line_status(line_id, limit=1):
    """获取产线最新状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM production_line_status
            WHERE line_id = %s
            ORDER BY collection_time DESC
            LIMIT %s
        """

        cursor.execute(query, (line_id, limit))
        status_data = cursor.fetchall()

        print(json.dumps({
            'success': True,
            'data': status_data
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取产线状态时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_production_line_with_status():
    """获取产线信息及其最新状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT pl.*,
                   pls.runtime_hours,
                   pls.real_time_capacity,
                   pls.noise_level,
                   pls.temperature,
                   pls.air_quality,
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
            'error': f'获取产线及状态时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_production_lines_by_foreman(foreman_id):
    """获取指定工长负责的产线列表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT pl.*,
                   pls.runtime_hours,
                   pls.real_time_capacity,
                   pls.noise_level,
                   pls.temperature,
                   pls.air_quality,
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
            WHERE pl.foreman_id = %s
        """

        cursor.execute(query, (foreman_id,))
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
            'error': f'获取工长负责产线时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def assign_foreman_to_line(line_id, foreman_id):
    """分配工长到产线"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 更新产线的负责工长
        query = "UPDATE production_line SET foreman_id = %s WHERE id = %s"
        cursor.execute(query, (foreman_id, line_id))
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': f'已成功将工长 {foreman_id} 分配给产线 {line_id}'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'分配工长到产线时出错: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_production_line_detail(line_id):
    """获取单个产线的详细信息及其最新状态和设备信息"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取产线基本信息及最新状态
        query = """
            SELECT pl.*,
                   pls.runtime_hours,
                   pls.real_time_capacity,
                   pls.noise_level,
                   pls.temperature,
                   pls.air_quality,
                   pls.collection_time,
                   u.username as foreman_name
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
            LEFT JOIN users u ON pl.foreman_id = u.employee_id
            WHERE pl.id = %s
        """

        cursor.execute(query, (line_id,))
        line_data = cursor.fetchone()

        if not line_data:
            print(json.dumps({
                'success': False,
                'error': f'未找到ID为{line_id}的产线'
            }, ensure_ascii=False))
            return

        # 处理JSON字段
        if 'equipment_list' in line_data and line_data['equipment_list']:
            try:
                if isinstance(line_data['equipment_list'], str):
                    line_data['equipment_list'] = json.loads(line_data['equipment_list'])
            except:
                pass  # 如果解析失败，保持原样

        # 获取产线上的设备信息
        equipment_query = """
            SELECT e.*, es.runtime_hours, es.fault_probability, es.collection_time, es.sensor_data,
                   u.username as worker_name
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
            LEFT JOIN users u ON e.worker_id = u.employee_id
            WHERE e.line_id = %s
        """

        cursor.execute(equipment_query, (line_id,))
        equipment_data = cursor.fetchall()

        # 处理设备的JSON字段
        for device in equipment_data:
            if 'sensor_data' in device and device['sensor_data']:
                try:
                    if isinstance(device['sensor_data'], str):
                        device['sensor_data'] = json.loads(device['sensor_data'])
                except:
                    pass  # 如果解析失败，保持原样

        # 组合结果
        result = {
            'line': line_data,
            'equipment': equipment_data
        }

        print(json.dumps({
            'success': True,
            'data': result
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取产线详情时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 主函数
# =============================================
def main():
    parser = argparse.ArgumentParser(description='产线管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 创建表命令
    create_parser = subparsers.add_parser('create-tables', help='创建产线相关表')
    create_parser.add_argument('--drop', action='store_true', help='删除现有表后重新创建')

    # 添加产线命令
    add_parser = subparsers.add_parser('add-line', help='添加新产线')
    add_parser.add_argument('--data', required=True, help='产线数据(JSON格式)')

    # 更新产线状态命令
    update_parser = subparsers.add_parser('update-status', help='更新产线状态')
    update_parser.add_argument('--line-id', required=True, type=int, help='产线ID')
    update_parser.add_argument('--data', required=True, help='状态数据(JSON格式)')

    # 获取产线列表命令
    list_parser = subparsers.add_parser('list', help='获取产线列表')

    # 获取工长负责的产线列表命令
    list_by_foreman_parser = subparsers.add_parser('list-by-foreman', help='获取工长负责的产线列表')
    list_by_foreman_parser.add_argument('--foreman-id', required=True, help='工长工号')

    # 分配工长到产线命令
    assign_foreman_parser = subparsers.add_parser('assign-foreman', help='分配工长到产线')
    assign_foreman_parser.add_argument('--line-id', required=True, type=int, help='产线ID')
    assign_foreman_parser.add_argument('--foreman-id', required=True, help='工长工号')

    # 获取产线状态命令
    status_parser = subparsers.add_parser('get-status', help='获取产线状态')
    status_parser.add_argument('--line-id', required=True, type=int, help='产线ID')
    status_parser.add_argument('--limit', type=int, default=1, help='返回记录数量')

    # 获取产线及其状态命令
    combined_parser = subparsers.add_parser('get-with-status', help='获取产线及其最新状态')

    # 获取单个产线详情命令
    detail_parser = subparsers.add_parser('get-detail', help='获取单个产线的详细信息')
    detail_parser.add_argument('--line-id', required=True, type=int, help='产线ID')

    args = parser.parse_args()

    if args.command == 'create-tables':
        create_production_line_tables(drop_existing=args.drop)
    elif args.command == 'add-line':
        try:
            line_data = json.loads(args.data)
            add_production_line(line_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'update-status':
        try:
            status_data = json.loads(args.data)
            update_production_line_status(args.line_id, status_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'list':
        get_production_line_list()
    elif args.command == 'list-by-foreman':
        get_production_lines_by_foreman(args.foreman_id)
    elif args.command == 'assign-foreman':
        assign_foreman_to_line(args.line_id, args.foreman_id)
    elif args.command == 'get-status':
        get_production_line_status(args.line_id, args.limit)
    elif args.command == 'get-with-status':
        get_production_line_with_status()
    elif args.command == 'get-detail':
        get_production_line_detail(args.line_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
