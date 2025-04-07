import sys
import json
import hashlib
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',  # 请修改为实际的数据库密码
            database='industry_db'
        )
        return connection
    except Error as e:
        print(json.dumps({
            'authenticated': False,
            'error': f'数据库连接错误: {str(e)}'
        }))
        sys.exit(1)

def register_user(username, password, role):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 检查用户名是否已存在
        check_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            print(json.dumps({
                'success': False,
                'error': '用户名已存在'
            }))
            return
        
        # 对密码进行哈希处理
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 插入新用户
        insert_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, hashed_password, role))
        connection.commit()
        
        print(json.dumps({
            'success': True,
            'message': '注册成功'
        }))
        
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'数据库错误: {str(e)}'
        }))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def verify_user(username, password, role):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 使用参数化查询防止SQL注入
        query = "SELECT * FROM users WHERE username = %s AND role = %s"
        cursor.execute(query, (username, role))
        user = cursor.fetchone()
        
        if user:
            # 对输入的密码进行哈希处理
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            if hashed_password == user['password']:
                print(json.dumps({
                    'authenticated': True,
                    'username': user['username'],
                    'role': user['role']
                }))
                return
        
        print(json.dumps({
            'authenticated': False,
            'error': '用户名或密码错误'
        }))
        
    except Error as e:
        print(json.dumps({
            'authenticated': False,
            'error': f'数据库查询错误: {str(e)}'
        }))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(json.dumps({
            'authenticated': False,
            'error': '参数错误'
        }))
        sys.exit(1)
    
    action = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    role = sys.argv[4] if len(sys.argv) > 4 else ''
    
    if action == 'verify':
        verify_user(username, password, role)
    elif action == 'register':
        register_user(username, password, role)
    else:
        print(json.dumps({
            'authenticated': False,
            'error': '无效的操作'
        }))