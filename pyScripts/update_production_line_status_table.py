#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error
import sys
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

def update_production_line_status_table():
    """更新产线状态表，添加噪音水平、环境温度和空气质量字段"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'industry_db' 
            AND TABLE_NAME = 'production_line_status'
        """)
        existing_columns = [column[0] for column in cursor.fetchall()]

        # 添加噪音水平字段
        if 'noise_level' not in existing_columns:
            cursor.execute("""
                ALTER TABLE production_line_status
                ADD COLUMN noise_level FLOAT COMMENT '噪音水平(dB)'
            """)
            print("已添加噪音水平字段")

        # 添加环境温度字段
        if 'temperature' not in existing_columns:
            cursor.execute("""
                ALTER TABLE production_line_status
                ADD COLUMN temperature FLOAT COMMENT '环境温度(°C)'
            """)
            print("已添加环境温度字段")

        # 添加空气质量字段
        if 'air_quality' not in existing_columns:
            cursor.execute("""
                ALTER TABLE production_line_status
                ADD COLUMN air_quality VARCHAR(20) COMMENT '空气质量(good/medium/poor)'
            """)
            print("已添加空气质量字段")

        connection.commit()
        print(json.dumps({
            'success': True,
            'message': '产线状态表更新成功，已添加噪音水平、环境温度和空气质量字段'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'更新产线状态表时出错: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    update_production_line_status_table()
