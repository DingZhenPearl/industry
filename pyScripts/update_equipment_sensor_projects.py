#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import argparse
import mysql.connector
from mysql.connector import Error
import io

# 设置输出编码
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
                sensor_projects = None

        print(json.dumps({
            'success': True,
            'data': {
                'equipment_id': equipment['id'],
                'equipment_name': equipment['equipment_name'],
                'sensor_projects': sensor_projects
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

def main():
    parser = argparse.ArgumentParser(description='更新设备传感器项目列表')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 更新传感器项目列表命令
    update_parser = subparsers.add_parser('update', help='更新传感器项目列表')
    update_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')
    update_parser.add_argument('--data', required=True, help='传感器项目列表(JSON格式)')

    # 获取传感器项目列表命令
    get_parser = subparsers.add_parser('get', help='获取传感器项目列表')
    get_parser.add_argument('--equipment-id', required=True, type=int, help='设备ID')

    args = parser.parse_args()

    if args.command == 'update':
        try:
            sensor_projects = json.loads(args.data)
            update_sensor_projects(args.equipment_id, sensor_projects)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': 'JSON解析错误，请检查数据格式'
            }, ensure_ascii=False))
    elif args.command == 'get':
        get_sensor_projects(args.equipment_id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
