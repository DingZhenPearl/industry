#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector

# 连接数据库
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='mwYgR7#*X2',
        database='industry_db'
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        # 查询equipment表结构
        cursor.execute("DESCRIBE equipment")
        print("Equipment表结构:")
        for row in cursor.fetchall():
            print(row)
        
except Exception as e:
    print(f"错误: {e}")
    
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("数据库连接已关闭")
