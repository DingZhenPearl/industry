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
            database='industry_db',
            charset='utf8mb4',
            use_unicode=True
        )
        return connection
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'数据库连接失败: {str(e)}'
        }, ensure_ascii=False))
        exit(1)

def update_user_status_field():
    """修改用户表的status字段为枚举类型，只允许三个值：在岗、离岗、请假"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 首先将现有的status值转换为新的枚举值
        cursor.execute("""
            UPDATE users
            SET status = CASE 
                WHEN status = 'active' THEN '在岗'
                WHEN status = 'off' THEN '离岗'
                WHEN status = 'leave' THEN '请假'
                ELSE '在岗'
            END
        """)
        
        # 修改status字段为枚举类型
        cursor.execute("""
            ALTER TABLE users
            MODIFY COLUMN status ENUM('在岗', '离岗', '请假') DEFAULT '在岗' COMMENT '员工状态'
        """)
        
        connection.commit()
        print(json.dumps({
            'success': True,
            'message': '用户表status字段修改成功'
        }, ensure_ascii=False))
    
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'修改用户表status字段失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    update_user_status_field()
