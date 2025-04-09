import json
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root', 
        password='123456',
        database='industry_db'
    )

def get_users():
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            employee_id as id,
            username as name,
            role,
            phone,
            status,
            CASE 
                WHEN status = 'active' THEN '在职'
                WHEN status = 'leave' THEN '请假'
                WHEN status = 'off' THEN '离职'
                ELSE '在职'
            END as statusText
        FROM users
        """
        cursor.execute(query)
        users = cursor.fetchall()
        print(json.dumps({
            'success': True,
            'data': users
        }, ensure_ascii=False))
            
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    get_users()
