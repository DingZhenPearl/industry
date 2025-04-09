import mysql.connector
from mysql.connector import Error

def get_db_connection():
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

def add_line_id_field():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = 'industry_db' 
            AND table_name = 'users' 
            AND column_name = 'lineId'
        """)
        if cursor.fetchone()[0] == 0:
            # 添加lineId字段
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN lineId INT DEFAULT 1 COMMENT '所属产线ID'
            """)
            print("成功添加lineId字段")
        else:
            print("lineId字段已存在")

        # 为所有用户分配默认产线
        cursor.execute("UPDATE users SET lineId = 1 WHERE lineId IS NULL")
        print(f"已更新 {cursor.rowcount} 条记录的默认产线")
        
        connection.commit()
        
    except Error as e:
        print(f"执行错误: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_line_id_field()
