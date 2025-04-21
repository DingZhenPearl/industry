#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
产线管理统一工具

本工具整合了产线管理相关的所有功能，包括：
1. 产线表的创建和管理
2. 产线信息的添加、更新、删除
3. 产线状态的更新和查询
4. 产线与工长的关联管理
5. 按组号、工长等条件查询产线

使用方法：
python production_line_unified.py <命令> [参数]

例如：
- 创建表：python production_line_unified.py create-tables
- 添加产线：python production_line_unified.py add-line --data '{"line_name": "一号生产线"}'
- 查询产线列表：python production_line_unified.py list

详细命令请使用 -h 或 --help 查看帮助信息。
"""

import json
import sys
import argparse
import mysql.connector
from mysql.connector import Error
import io
from datetime import datetime

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 日期时间JSON编码器
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

# =============================================
# 产线表创建和基本管理功能
# =============================================

def create_production_line_tables(drop_existing=False):
    """创建产线相关的数据表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if drop_existing:
            # 删除现有表
            cursor.execute("DROP TABLE IF EXISTS production_line_status")
            cursor.execute("DROP TABLE IF EXISTS production_line")

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
                runtime_hours FLOAT COMMENT '运行时长(小时)',
                real_time_capacity FLOAT COMMENT '实时产能',
                noise_level FLOAT NULL COMMENT '噪音水平(dB)',
                temperature FLOAT NULL COMMENT '温度(°C)',
                air_quality FLOAT NULL COMMENT '空气质量指数',
                collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
                INDEX idx_line_id (line_id),
                INDEX idx_collection_time (collection_time),
                FOREIGN KEY (line_id) REFERENCES production_line(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产线实时状态表'
        """)

        print(json.dumps({
            'success': True,
            'message': '产线相关表创建成功'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'创建表时出错: {str(e)}'
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

        # 检查必要字段
        if 'line_name' not in line_data:
            print(json.dumps({
                'success': False,
                'error': '缺少必要字段: line_name'
            }, ensure_ascii=False))
            return

        # 准备设备列表字段
        if 'equipment_list' in line_data and isinstance(line_data['equipment_list'], list):
            line_data['equipment_list'] = json.dumps(line_data['equipment_list'], ensure_ascii=False)

        # 构建插入语句
        fields = []
        placeholders = []
        values = []

        for key, value in line_data.items():
            fields.append(key)
            placeholders.append('%s')
            values.append(value)

        query = f"""
            INSERT INTO production_line ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        connection.commit()

        # 获取新插入的产线ID
        line_id = cursor.lastrowid

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
        if connection:
            connection.rollback()
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

        # 检查产线是否存在
        cursor.execute("SELECT id FROM production_line WHERE id = %s", (line_id,))
        if not cursor.fetchone():
            print(json.dumps({
                'success': False,
                'error': f'未找到ID为{line_id}的产线'
            }, ensure_ascii=False))
            return

        # 构建插入语句
        fields = ['line_id']
        placeholders = ['%s']
        values = [line_id]

        for key, value in status_data.items():
            fields.append(key)
            placeholders.append('%s')
            values.append(value)

        query = f"""
            INSERT INTO production_line_status ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        connection.commit()

        # 获取新插入的状态记录ID
        status_id = cursor.lastrowid

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
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 产线查询和获取功能
# =============================================

def get_production_line_list():
    """获取产线列表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM production_line"
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
            'error': f'获取产线列表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_production_line_status(line_id, limit=1):
    """获取产线状态数据"""
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
    """获取产线及其最新状态"""
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

        # 获取产线上的设备及其最新状态和负责人信息
        query_equipment = """
            SELECT e.*,
                   es.runtime_hours,
                   es.fault_probability,
                   es.collection_time as status_update_time,
                   u.username as worker_name,
                   u.phone as worker_phone
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

        cursor.execute(query_equipment, (line_id,))
        equipment_data = cursor.fetchall()

        # 获取产线状态历史记录
        query_history = """
            SELECT *
            FROM production_line_status
            WHERE line_id = %s
            ORDER BY collection_time DESC
            LIMIT 10
        """

        cursor.execute(query_history, (line_id,))
        history_data = cursor.fetchall()

        result = {
            'line': line_data,
            'equipment': equipment_data,
            'history': history_data
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
# 产线管理和分组功能
# =============================================

def assign_foreman_to_line(line_id, foreman_id):
    """分配工长到产线"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查产线是否存在
        cursor.execute("SELECT id FROM production_line WHERE id = %s", (line_id,))
        if not cursor.fetchone():
            print(json.dumps({
                'success': False,
                'error': f'未找到ID为{line_id}的产线'
            }, ensure_ascii=False))
            return

        # 检查工长是否存在
        cursor.execute("SELECT employee_id FROM users WHERE employee_id = %s AND role = 'foreman'", (foreman_id,))
        if not cursor.fetchone():
            print(json.dumps({
                'success': False,
                'error': f'未找到工号为{foreman_id}的工长'
            }, ensure_ascii=False))
            return

        # 更新产线的工长工号
        cursor.execute("UPDATE production_line SET foreman_id = %s WHERE id = %s", (foreman_id, line_id))
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': f'工长{foreman_id}已成功分配到产线{line_id}'
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
            line['foreman'] = None
            foreman_id = line['foreman_id']

            if foreman_id:
                for foreman in foremen:
                    if foreman['id'] == foreman_id:
                        line['foreman'] = foreman
                        break

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

# =============================================
# 产线更新和删除功能
# =============================================

def update_production_line(line_id, line_data):
    """更新产线静态信息，包括状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 构建更新语句
        set_clauses = []
        values = []

        for key, value in line_data.items():
            if key not in ['id', 'created_at', 'updated_at']:  # 跳过自动生成的字段
                set_clauses.append(f"{key} = %s")
                values.append(value)

        # 添加line_id到values列表
        values.append(line_id)

        query = f"""
            UPDATE production_line
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """

        cursor.execute(query, values)
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '产线信息更新成功'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'更新产线信息时出错: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

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

    # 更新产线静态信息命令
    update_line_parser = subparsers.add_parser('update-line', help='更新产线静态信息')
    update_line_parser.add_argument('--line-id', required=True, type=int, help='产线ID')
    update_line_parser.add_argument('--data', required=True, help='更新数据(JSON格式)')

    # 删除产线命令
    delete_parser = subparsers.add_parser('delete-line', help='删除产线')
    delete_parser.add_argument('--line-id', required=True, type=int, help='产线ID')

    # 获取产线列表命令
    list_parser = subparsers.add_parser('list', help='获取产线列表')

    # 获取工长负责的产线列表命令
    list_by_foreman_parser = subparsers.add_parser('list-by-foreman', help='获取工长负责的产线列表')
    list_by_foreman_parser.add_argument('--foreman-id', required=True, help='工长工号')

    # 获取组号对应的产线列表命令
    list_by_group_parser = subparsers.add_parser('list-by-group', help='获取组号对应的产线列表')
    list_by_group_parser.add_argument('--group-id', required=True, help='组号')

    # 分配工长到产线命令
    assign_foreman_parser = subparsers.add_parser('assign-foreman', help='分配工长到产线')
    assign_foreman_parser.add_argument('--line-id', required=True, type=int, help='产线ID')
    assign_foreman_parser.add_argument('--foreman-id', required=True, help='工长工号')

    # 获取产线状态命令
    status_parser = subparsers.add_parser('get-status', help='获取产线状态')
    status_parser.add_argument('--line-id', required=True, type=int, help='产线ID')
    status_parser.add_argument('--limit', type=int, default=1, help='返回记录数量')

    # 获取产线及状态命令
    with_status_parser = subparsers.add_parser('get-with-status', help='获取产线及状态')

    # 获取产线及工长信息命令
    with_foremen_parser = subparsers.add_parser('get-with-foremen', help='获取产线及工长信息')

    # 获取产线详情命令
    detail_parser = subparsers.add_parser('get-detail', help='获取产线详情')
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
    elif args.command == 'update-line':
        try:
            line_data = json.loads(args.data)
            update_production_line(args.line_id, line_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'delete-line':
        delete_production_line(args.line_id)
    elif args.command == 'list':
        get_production_line_list()
    elif args.command == 'list-by-foreman':
        get_production_lines_by_foreman(args.foreman_id)
    elif args.command == 'list-by-group':
        get_production_lines_by_group(args.group_id)
    elif args.command == 'assign-foreman':
        assign_foreman_to_line(args.line_id, args.foreman_id)
    elif args.command == 'get-status':
        get_production_line_status(args.line_id, args.limit)
    elif args.command == 'get-with-status':
        get_production_line_with_status()
    elif args.command == 'get-with-foremen':
        get_production_lines_with_foremen()
    elif args.command == 'get-detail':
        get_production_line_detail(args.line_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
