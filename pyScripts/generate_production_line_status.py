#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error
import random
import datetime
import time
import sys
import io
from datetime import datetime, timedelta

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

def get_production_lines():
    """获取所有产线信息"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT id, line_name, theoretical_capacity FROM production_line"
        cursor.execute(query)
        lines = cursor.fetchall()
        
        return lines
    except Error as e:
        print(f"获取产线信息出错: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def generate_status_data(line, num_records=24, interval_hours=1):
    """为指定产线生成状态数据"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 获取当前时间
        now = datetime.now()
        
        # 生成过去24小时的数据，每小时一条
        for i in range(num_records):
            # 计算数据采集时间
            collection_time = now - timedelta(hours=i * interval_hours)
            
            # 生成随机运行时长（累计值，随时间增加）
            base_runtime = 1000 + (line['id'] * 100)  # 基础运行时长
            runtime_hours = base_runtime + (num_records - i) * interval_hours
            
            # 生成随机实时产能（理论产能的70%-95%之间，有波动）
            efficiency = 0.7 + (random.random() * 0.25)
            real_time_capacity = line['theoretical_capacity'] * efficiency
            
            # 插入数据
            query = """
                INSERT INTO production_line_status 
                (line_id, runtime_hours, real_time_capacity, collection_time)
                VALUES (%s, %s, %s, %s)
            """
            values = (line['id'], runtime_hours, real_time_capacity, collection_time)
            
            cursor.execute(query, values)
        
        connection.commit()
        print(f"已为产线 {line['line_name']} 生成 {num_records} 条状态数据")
        
    except Error as e:
        print(f"生成产线状态数据出错: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def clear_status_data():
    """清空产线状态表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "TRUNCATE TABLE production_line_status"
        cursor.execute(query)
        connection.commit()
        
        print("已清空产线状态表")
    except Error as e:
        print(f"清空产线状态表出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    # 清空现有数据
    clear_status_data()
    
    # 获取所有产线
    lines = get_production_lines()
    
    if not lines:
        print("未找到产线信息，请先添加产线")
        return
    
    # 为每条产线生成状态数据
    for line in lines:
        generate_status_data(line)
    
    print("产线状态数据生成完成")

if __name__ == "__main__":
    main()
