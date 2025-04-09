import mysql.connector
import hashlib

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='mwYgR7#*X2',
        database='industry_db'
    )

def add_employee_id_field():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 添加工号字段
        cursor.execute("ALTER TABLE users ADD employee_id VARCHAR(20) UNIQUE")
        
        # 获取所有用户
        cursor.execute("SELECT id, role FROM users")
        users = cursor.fetchall()
        
        # 为每个用户生成并更新工号
        for user_id, role in users:
            # 根据角色生成工号前缀
            prefix = {
                'supervisor': 'SP',
                'foreman': 'FM',
                'member': 'WK',
                'safety_officer': 'SF'
            }.get(role, 'EMP')
            
            # 生成工号 (前缀 + 4位数字)
            employee_id = f"{prefix}{user_id:04d}"
            
            # 更新用户的工号
            cursor.execute(
                "UPDATE users SET employee_id = %s WHERE id = %s",
                (employee_id, user_id)
            )
        
        connection.commit()
        print("工号字段添加成功")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    add_employee_id_field()
