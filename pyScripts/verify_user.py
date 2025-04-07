import sys
import json
import hashlib
import mysql.connector
from mysql.connector import Error
import io

# 在文件开头添加编码设置
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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

def update_username(new_username, role, current_username):
    connection = None
    try:
        # 调试信息输出到stderr，不影响stdout的JSON输出
        print(f"尝试更新用户名: {current_username} -> {new_username}, 角色: {role}", file=sys.stderr)
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 检查新用户名是否已存在且不是当前用户
        check_query = "SELECT * FROM users WHERE username = %s AND username != %s"
        cursor.execute(check_query, (new_username, current_username))
        if cursor.fetchone():
            error_msg = f"用户名 {new_username} 已存在"
            print(json.dumps({
                'success': False,
                'error': error_msg
            }))
            return
        
        # 更新用户名
        update_query = "UPDATE users SET username = %s WHERE username = %s AND role = %s"
        cursor.execute(update_query, (new_username, current_username, role))
        connection.commit()
        
        if cursor.rowcount > 0:
            result = {
                'success': True,
                'message': '用户名更新成功'
            }
        else:
            result = {
                'success': False,
                'error': f"未找到用户 {current_username} 或角色不匹配"
            }
        
        # 确保输出UTF-8编码的JSON
        json.dump(result, sys.stdout, ensure_ascii=False)
        print()  # 添加换行符
        
    except Exception as e:
        error_msg = f"数据库操作异常: {str(e)}"
        print(error_msg, file=sys.stderr)
        json.dump({
            'success': False,
            'error': error_msg
        }, sys.stdout, ensure_ascii=False)
        print()  # 添加换行符
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_password(username, role, new_password):
    try:
        # 调试信息输出到stderr
        print(f"尝试更新密码: 用户={username}, 角色={role}", file=sys.stderr)
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 更新密码
        new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
        update_query = "UPDATE users SET password = %s WHERE username = %s AND role = %s"
        cursor.execute(update_query, (new_hashed, username, role))
        connection.commit()
        
        # 只输出JSON到stdout
        json.dump({
            'success': True,
            'message': '密码更新成功'
        }, sys.stdout, ensure_ascii=False)
        print()  # 添加换行符
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'密码更新失败: {str(e)}'
        }), file=sys.stderr)
        sys.exit(1)
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
    if len(sys.argv) < 5:
        print(json.dumps({
            'success': False,
            'error': '参数不足'
        }))
        sys.exit(1)
    
    action = sys.argv[1]
    username = sys.argv[2]  # 第一个参数是用户名
    role = sys.argv[3]      # 第二个参数是角色
    
    if action == 'update_password':
        if len(sys.argv) < 5:
            print(json.dumps({
                'success': False,
                'error': '缺少密码参数'
            }))
            sys.exit(1)
        new_password = sys.argv[4]  # 第四个参数是新密码
        update_password(username, role, new_password)
    elif action == 'verify':
        verify_user(username, role, sys.argv[4])
    elif action == 'register':
        register_user(username, role, sys.argv[4])
    elif action == 'update_username':
        new_username = sys.argv[4] if len(sys.argv) > 4 else ''
        if not new_username:
            print(json.dumps({
                'success': False,
                'error': '缺少新用户名参数'
            }))
            sys.exit(1)
        update_username(new_username, role, username)
    else:
        print(json.dumps({
            'success': False,
            'error': '无效的操作'
        }))