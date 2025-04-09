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
        
        # 获取最后一个ID用于生成工号
        cursor.execute("SELECT MAX(id) as max_id FROM users")
        result = cursor.fetchone()
        next_id = (result['max_id'] or 0) + 1
        
        # 根据角色生成工号前缀
        prefix = {
            'supervisor': 'SP',
            'foreman': 'FM',
            'member': 'WK',
            'safety_officer': 'SF'
        }.get(role, 'EMP')
        
        employee_id = f"{prefix}{next_id:04d}"
        
        # 插入新用户时包含工号
        insert_query = "INSERT INTO users (username, password, role, employee_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (username, hashed_password, role, employee_id))
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
        check_query = """
            SELECT username, password, role, phone, employee_id, group_id 
            FROM users WHERE username = %s AND role = %s
        """
        cursor.execute(check_query, (username, role))
        user = cursor.fetchone()
        
        if user and hashlib.sha256(password.encode()).hexdigest() == user['password']:
            print(json.dumps({
                'authenticated': True,
                'username': user['username'],
                'role': user['role'],
                'phone': user['phone'],
                'employee_id': user['employee_id'],
                'group_id': user['group_id']
            }))
            return
        
        print(json.dumps({
            'authenticated': False,
            'error': '用户名或密码错误'
        }))
            
    except Error as e:
        print(json.dumps({
            'authenticated': False,
            'error': str(e)
        }))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_user(username, role, phone):
    connection = None
    try:
        # 验证手机号格式
        if not phone or len(phone) != 11 or not phone.isdigit():
            print(json.dumps({
                'success': False,
                'error': '请输入有效的11位手机号'
            }))
            return
            
        connection = get_db_connection()
        cursor = connection.cursor()
        
        update_query = "UPDATE users SET phone = %s WHERE username = %s AND role = %s"
        cursor.execute(update_query, (phone, username, role))
        connection.commit()
        
        print(json.dumps({
            'success': True,
            'message': '手机号更新成功'
        }))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'手机号更新失败: {str(e)}'
        }))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_group_id(username, role, group_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        update_query = "UPDATE users SET group_id = %s WHERE username = %s AND role = %s"
        cursor.execute(update_query, (group_id, username, role))
        connection.commit()
        
        print(json.dumps({
            'success': True,
            'message': '组号更新成功'
        }))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'组号更新失败: {str(e)}'
        }))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_users():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                employee_id as id,
                username as name,
                role,
                phone,
                group_id,
                COALESCE(status, 'active') as status,
                CASE 
                    WHEN status = 'leave' THEN '请假'
                    WHEN status = 'off' THEN '离岗' 
                    ELSE '在岗'
                END as statusText
            FROM users
        """
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        # 包装在success对象中返回
        print(json.dumps({
            'success': True,
            'data': users
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_team_members(group_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                employee_id as id,
                username as name,
                role,
                phone,
                group_id,
                COALESCE(status, 'active') as status,
                CASE 
                    WHEN status = 'leave' THEN '请假'
                    WHEN status = 'task' THEN '任务中'
                    WHEN status = 'off' THEN '离岗' 
                    ELSE '在岗'
                END as statusText
            FROM users
            WHERE group_id = %s AND role != 'supervisor' AND role != 'foreman'
        """
        
        cursor.execute(query, (group_id,))
        members = cursor.fetchall()
        
        # 确保所有字段都有值并添加默认的lineId
        processed_members = []
        for member in members:
            # 添加默认lineId值
            member['lineId'] = '1'  # 默认分配到1号产线
            processed_member = {}
            for key, value in member.items():
                if value is None:
                    processed_member[key] = ''
                else:
                    processed_member[key] = str(value)
            processed_members.append(processed_member)
        
        result = {
            'success': True,
            'data': processed_members
        }
        
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': '参数不足'
        }))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'get_users':
        get_users()
    elif action == 'get_team_members':
        group_id = sys.argv[2]
        get_team_members(group_id)
    elif len(sys.argv) < 4:
        print(json.dumps({
            'success': False,
            'error': '参数不足'
        }))
        sys.exit(1)
    else:
        username = sys.argv[2]
        role = sys.argv[3]
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
        elif action == 'update_user':
            phone = sys.argv[4] if len(sys.argv) > 4 else ''
            if not phone:
                print(json.dumps({
                    'success': False,
                    'error': '缺少电话号码参数'
                }))
                sys.exit(1)
            update_user(username, role, phone)
        elif action == 'update_group':
            group_id = sys.argv[4] if len(sys.argv) > 4 else ''
            update_group_id(username, role, group_id)
        else:
            print(json.dumps({
                'success': False,
                'error': '无效的操作'
            }))