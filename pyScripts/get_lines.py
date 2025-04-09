import sys
import json
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
        print(f"数据库连接错误: {e}")
        return None

def get_assigned_lines(group_id):
    """获取指定组号对应的产线列表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 查询该组号对应的产线
        query = """
            SELECT DISTINCT line_id as id, 
                   CASE 
                       WHEN line_id = 1 THEN '一号生产线'
                       WHEN line_id = 2 THEN '二号生产线'
                       WHEN line_id = 3 THEN '三号生产线'
                       ELSE CONCAT('产线-', line_id)
                   END as name
            FROM users
            WHERE group_id = %s AND line_id IS NOT NULL
            ORDER BY line_id
        """
        
        cursor.execute(query, (group_id,))
        lines = cursor.fetchall()
        
        # 如果没有找到产线，添加默认产线
        if not lines:
            lines = [
                {'id': 1, 'name': '一号生产线'},
                {'id': 2, 'name': '二号生产线'},
                {'id': 3, 'name': '三号生产线'}
            ]
        
        return {
            'success': True,
            'data': lines
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': '缺少组号参数'
        }))
        sys.exit(1)
        
    group_id = sys.argv[1]
    result = get_assigned_lines(group_id)
    print(json.dumps(result))
