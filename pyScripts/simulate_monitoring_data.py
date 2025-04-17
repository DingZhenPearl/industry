#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import mysql.connector
from mysql.connector import Error
import io
import time
import random
import math
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
# 模拟设备状态数据
# =============================================
def generate_equipment_status(equipment_id, runtime_base):
    """生成模拟的设备状态数据"""
    # 添加一些随机波动
    noise = random.uniform(-0.1, 0.1)
    runtime_hours = runtime_base + noise
    
    # 生成模拟的传感器数据
    sensor_data = {
        "temperature": round(random.uniform(60, 90), 1),  # 温度在60-90°C之间波动
        "pressure": round(random.uniform(15, 22), 2),     # 压力在15-22MPa之间波动
        "speed": round(random.uniform(800, 900)),         # 转速在800-900rpm之间波动
        "vibration": round(random.uniform(0.02, 0.08), 3) # 振动在0.02-0.08mm/s之间波动
    }
    
    # 根据温度和振动计算故障概率
    temp_factor = max(0, (sensor_data["temperature"] - 70) / 30)  # 温度超过70°C开始增加故障概率
    vibration_factor = max(0, (sensor_data["vibration"] - 0.05) / 0.05)  # 振动超过0.05mm/s开始增加故障概率
    fault_probability = round(min(0.9, 0.1 + 0.4 * temp_factor + 0.5 * vibration_factor), 3)
    
    return {
        "runtime_hours": runtime_hours,
        "sensor_data": sensor_data,
        "fault_probability": fault_probability
    }

# =============================================
# 模拟产线状态数据
# =============================================
def generate_production_line_status(line_id, runtime_base, theoretical_capacity):
    """生成模拟的产线状态数据"""
    # 添加一些随机波动
    noise = random.uniform(-0.1, 0.1)
    runtime_hours = runtime_base + noise
    
    # 生成模拟的实时产能，在理论产能的70%-95%之间波动
    efficiency = random.uniform(0.7, 0.95)
    real_time_capacity = round(theoretical_capacity * efficiency)
    
    return {
        "runtime_hours": runtime_hours,
        "real_time_capacity": real_time_capacity
    }

# =============================================
# 更新设备状态
# =============================================
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
        connection.commit()

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 设备 {equipment_id} 状态更新成功")
        return True

    except Error as e:
        print(f"更新设备状态时出错: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 更新产线状态
# =============================================
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
        connection.commit()

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 产线 {line_id} 状态更新成功")
        return True

    except Error as e:
        print(f"更新产线状态时出错: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 获取产线理论产能
# =============================================
def get_production_line_capacity(line_id):
    """获取产线的理论产能"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT theoretical_capacity FROM production_line
            WHERE id = %s
        """

        cursor.execute(query, (line_id,))
        result = cursor.fetchone()

        if result:
            return result['theoretical_capacity']
        else:
            print(f"未找到产线 {line_id} 的信息")
            return 1000  # 默认值
    except Error as e:
        print(f"获取产线信息时出错: {e}")
        return 1000  # 默认值
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 获取设备最新运行时间
# =============================================
def get_latest_runtime(table, id_field, id_value):
    """获取最新的运行时间"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = f"""
            SELECT runtime_hours FROM {table}
            WHERE {id_field} = %s
            ORDER BY collection_time DESC
            LIMIT 1
        """

        cursor.execute(query, (id_value,))
        result = cursor.fetchone()

        if result:
            return result['runtime_hours']
        else:
            print(f"未找到 {table} 表中 {id_field}={id_value} 的最新运行时间")
            return 0  # 默认值
    except Error as e:
        print(f"获取最新运行时间时出错: {e}")
        return 0  # 默认值
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 主函数
# =============================================
def main():
    """主函数，每10秒生成一次模拟数据"""
    # 设备ID和产线ID
    equipment_id = 6  # 包装机H-01的ID
    line_id = 3       # 三号产线的ID
    
    print(f"开始模拟监控数据生成，目标设备ID: {equipment_id}，产线ID: {line_id}")
    print(f"按Ctrl+C停止模拟")
    
    try:
        while True:
            # 获取最新的运行时间作为基准
            equipment_runtime_base = get_latest_runtime("equipment_status", "equipment_id", equipment_id)
            line_runtime_base = get_latest_runtime("production_line_status", "line_id", line_id)
            
            # 获取产线理论产能
            theoretical_capacity = get_production_line_capacity(line_id)
            
            # 生成并更新设备状态
            equipment_status = generate_equipment_status(equipment_id, equipment_runtime_base + 0.003)  # 每10秒增加约0.003小时
            update_equipment_status(equipment_id, equipment_status)
            
            # 生成并更新产线状态
            line_status = generate_production_line_status(line_id, line_runtime_base + 0.003, theoretical_capacity)
            update_production_line_status(line_id, line_status)
            
            # 等待10秒
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n模拟已停止")

if __name__ == "__main__":
    main()
