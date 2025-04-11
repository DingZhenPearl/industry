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

def get_equipment():
    """获取所有设备信息"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT id, equipment_name, equipment_type FROM equipment"
        cursor.execute(query)
        equipment = cursor.fetchall()
        
        return equipment
    except Error as e:
        print(f"获取设备信息出错: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def generate_sensor_data(equipment_type):
    """根据设备类型生成传感器数据"""
    sensor_data = {}
    
    # 基础传感器数据（所有设备都有）
    sensor_data["temperature"] = round(random.uniform(20, 85), 1)  # 温度 (°C)
    sensor_data["vibration"] = round(random.uniform(0.1, 5.0), 2)  # 振动 (mm/s)
    sensor_data["noise"] = round(random.uniform(60, 95), 1)  # 噪音 (dB)
    
    # 根据设备类型添加特定传感器数据
    if "注塑机" in equipment_type:
        sensor_data["pressure"] = round(random.uniform(10, 30), 1)  # 压力 (MPa)
        sensor_data["mold_temperature"] = round(random.uniform(150, 250), 1)  # 模具温度 (°C)
        sensor_data["cycle_time"] = round(random.uniform(15, 45), 1)  # 周期时间 (s)
    
    elif "压铸机" in equipment_type:
        sensor_data["pressure"] = round(random.uniform(20, 50), 1)  # 压力 (MPa)
        sensor_data["metal_temperature"] = round(random.uniform(600, 750), 1)  # 金属温度 (°C)
        sensor_data["cycle_time"] = round(random.uniform(30, 90), 1)  # 周期时间 (s)
    
    elif "车床" in equipment_type or "铣床" in equipment_type:
        sensor_data["spindle_speed"] = round(random.uniform(500, 3000), 0)  # 主轴转速 (rpm)
        sensor_data["feed_rate"] = round(random.uniform(50, 300), 1)  # 进给速度 (mm/min)
        sensor_data["cutting_force"] = round(random.uniform(100, 500), 1)  # 切削力 (N)
    
    elif "组装" in equipment_type:
        sensor_data["air_pressure"] = round(random.uniform(0.4, 0.8), 2)  # 气压 (MPa)
        sensor_data["cycle_time"] = round(random.uniform(20, 120), 1)  # 周期时间 (s)
    
    elif "包装" in equipment_type:
        sensor_data["speed"] = round(random.uniform(10, 50), 1)  # 包装速度 (件/分钟)
        sensor_data["film_tension"] = round(random.uniform(10, 30), 1)  # 膜张力 (N)
    
    return sensor_data

def calculate_fault_probability(sensor_data, equipment_type):
    """根据传感器数据计算故障概率"""
    probability = 0.0
    
    # 基础故障概率（随机小值）
    base_probability = random.uniform(0.01, 0.1)
    probability += base_probability
    
    # 根据温度增加故障概率
    if sensor_data.get("temperature", 0) > 75:
        probability += (sensor_data["temperature"] - 75) * 0.02
    
    # 根据振动增加故障概率
    if sensor_data.get("vibration", 0) > 3.0:
        probability += (sensor_data["vibration"] - 3.0) * 0.05
    
    # 根据设备类型的特定传感器数据增加故障概率
    if "注塑机" in equipment_type or "压铸机" in equipment_type:
        if sensor_data.get("pressure", 0) > 25:
            probability += (sensor_data["pressure"] - 25) * 0.01
    
    elif "车床" in equipment_type or "铣床" in equipment_type:
        if sensor_data.get("spindle_speed", 0) > 2500:
            probability += (sensor_data["spindle_speed"] - 2500) * 0.0005
    
    # 确保概率在0-1之间
    probability = min(max(probability, 0.0), 1.0)
    
    return round(probability, 3)

def generate_status_data(equipment, num_records=24, interval_hours=1):
    """为指定设备生成状态数据"""
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
            base_runtime = 500 + (equipment['id'] * 50)  # 基础运行时长
            runtime_hours = base_runtime + (num_records - i) * interval_hours
            
            # 生成传感器数据
            sensor_data = generate_sensor_data(equipment['equipment_type'])
            
            # 计算故障概率
            fault_probability = calculate_fault_probability(sensor_data, equipment['equipment_type'])
            
            # 插入数据
            query = """
                INSERT INTO equipment_status 
                (equipment_id, runtime_hours, collection_time, sensor_data, fault_probability)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                equipment['id'], 
                runtime_hours, 
                collection_time, 
                json.dumps(sensor_data), 
                fault_probability
            )
            
            cursor.execute(query, values)
        
        connection.commit()
        print(f"已为设备 {equipment['equipment_name']} 生成 {num_records} 条状态数据")
        
    except Error as e:
        print(f"生成设备状态数据出错: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def clear_status_data():
    """清空设备状态表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = "TRUNCATE TABLE equipment_status"
        cursor.execute(query)
        connection.commit()
        
        print("已清空设备状态表")
    except Error as e:
        print(f"清空设备状态表出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    # 清空现有数据
    clear_status_data()
    
    # 获取所有设备
    equipment_list = get_equipment()
    
    if not equipment_list:
        print("未找到设备信息，请先添加设备")
        return
    
    # 为每个设备生成状态数据
    for equipment in equipment_list:
        generate_status_data(equipment)
    
    print("设备状态数据生成完成")

if __name__ == "__main__":
    main()
