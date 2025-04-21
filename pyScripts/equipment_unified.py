#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设备管理统一脚本
包含设备的增删改查、状态更新、工人分配等功能
"""

import json
import sys
import argparse
import mysql.connector
from mysql.connector import Error
import io
from datetime import datetime, date

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 用于JSON序列化datetime对象的编码器
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
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
                sensor_projects JSON COMMENT '传感器项目列表',
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
        if connection:
            connection.rollback()
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

        # 处理JSON字段
        if 'sensor_projects' in equipment_data and isinstance(equipment_data['sensor_projects'], dict):
            equipment_data['sensor_projects'] = json.dumps(equipment_data['sensor_projects'], ensure_ascii=False)

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
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

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
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

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

# =============================================
# 设备查询函数
# =============================================
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

# =============================================
# 传感器项目相关函数
# =============================================
def update_sensor_projects(equipment_id, sensor_projects):
    """更新设备的传感器项目列表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 将传感器项目列表转换为JSON字符串
        sensor_projects_json = json.dumps(sensor_projects, ensure_ascii=False)

        # 更新设备的sensor_projects字段
        query = """
            UPDATE equipment
            SET sensor_projects = %s
            WHERE id = %s
        """
        cursor.execute(query, (sensor_projects_json, equipment_id))
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '成功更新设备传感器项目列表',
            'equipment_id': equipment_id
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'更新传感器项目列表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_sensor_projects(equipment_id):
    """获取设备的传感器项目列表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查询设备的sensor_projects字段
        query = """
            SELECT id, equipment_name, sensor_projects
            FROM equipment
            WHERE id = %s
        """
        cursor.execute(query, (equipment_id,))
        equipment = cursor.fetchone()

        if not equipment:
            print(json.dumps({
                'success': False,
                'error': f'未找到ID为{equipment_id}的设备'
            }, ensure_ascii=False))
            return

        # 解析JSON字段
        sensor_projects = None
        if equipment['sensor_projects']:
            try:
                if isinstance(equipment['sensor_projects'], str):
                    sensor_projects = json.loads(equipment['sensor_projects'])
                else:
                    sensor_projects = equipment['sensor_projects']
            except:
                sensor_projects = {}  # 如果解析失败，返回空对象

        print(json.dumps({
            'success': True,
            'data': {
                'equipment_id': equipment['id'],
                'equipment_name': equipment['equipment_name'],
                'sensor_projects': sensor_projects or {}
            }
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取传感器项目列表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 主函数
# =============================================
def main():
    parser = argparse.ArgumentParser(description='设备管理统一工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 创建表命令
    create_parser = subparsers.add_parser('create-tables', help='创建设备相关表')
    create_parser.add_argument('--drop', action='store_true', help='删除现有表后重新创建')

    # 添加设备命令
    add_parser = subparsers.add_parser('add-equipment', help='添加新设备')
    add_parser.add_argument('--data', required=True, help='设备数据(JSON格式)')

    # 更新设备状态命令
    update_status_parser = subparsers.add_parser('update-status', help='更新设备状态')
    update_status_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')
    update_status_parser.add_argument('--data', required=True, help='状态数据(JSON格式)')

    # 更新设备静态信息命令
    update_parser = subparsers.add_parser('update-equipment', help='更新设备静态信息')
    update_parser.add_argument('--equipment-id', required=True, help='设备ID')
    update_parser.add_argument('--data', required=True, help='更新的数据，JSON格式')

    # 删除设备命令
    delete_parser = subparsers.add_parser('delete-equipment', help='删除设备')
    delete_parser.add_argument('--equipment-id', required=True, help='设备ID')

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

    # 获取设备及其负责工人命令
    with_workers_parser = subparsers.add_parser('get-with-workers', help='获取设备及其负责工人')
    with_workers_parser.add_argument('--line-id', help='按产线ID筛选')

    # 按组号获取设备命令
    by_group_parser = subparsers.add_parser('get-by-group', help='按组号获取设备')
    by_group_parser.add_argument('group_id', help='组号')

    # 更新传感器项目命令
    update_sensor_parser = subparsers.add_parser('update-sensor-projects', help='更新传感器项目')
    update_sensor_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')
    update_sensor_parser.add_argument('--data', required=True, help='传感器项目数据(JSON格式)')

    # 获取传感器项目命令
    get_sensor_parser = subparsers.add_parser('get-sensor-projects', help='获取传感器项目')
    get_sensor_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')

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
    elif args.command == 'update-equipment':
        try:
            equipment_data = json.loads(args.data)
            update_equipment(args.equipment_id, equipment_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'delete-equipment':
        delete_equipment(args.equipment_id)
    elif args.command == 'assign-worker':
        assign_worker_to_equipment(args.equipment_id, args.worker_id)
    elif args.command == 'list':
        get_equipment_list(args.line_id, args.status)
    elif args.command == 'get-status':
        get_equipment_status(args.equipment_id, args.limit)
    elif args.command == 'get-with-status':
        get_equipment_with_status(args.line_id, args.equipment_id)
    elif args.command == 'get-with-workers':
        get_equipment_with_workers(args.line_id)
    elif args.command == 'get-by-group':
        get_equipment_by_group(args.group_id)
    elif args.command == 'update-sensor-projects':
        try:
            sensor_projects = json.loads(args.data)
            update_sensor_projects(args.equipment_id, sensor_projects)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'get-sensor-projects':
        get_sensor_projects(args.equipment_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
