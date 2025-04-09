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

        # 检查字段是否已存在 - 修改为检查line_id而非lineId
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = 'industry_db' 
            AND table_name = 'users' 
            AND column_name = 'line_id'
        """)
        if cursor.fetchone()[0] == 0:
            # 添加line_id字段 - 修改为添加line_id而非lineId
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN line_id INT DEFAULT 1 COMMENT '所属产线ID'
            """)
            print("成功添加line_id字段")
        else:
            print("line_id字段已存在")

        # 移除多余的lineId字段(如果存在)
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = 'industry_db' 
            AND table_name = 'users' 
            AND column_name = 'lineId'
        """)
        if cursor.fetchone()[0] > 0:
            # 如果lineId存在，则将数据合并到line_id中，然后删除lineId
            cursor.execute("UPDATE users SET line_id = lineId WHERE line_id IS NULL AND lineId IS NOT NULL")
            cursor.execute("ALTER TABLE users DROP COLUMN lineId")
            print("已移除多余的lineId字段")

        # 为所有用户分配默认产线
        cursor.execute("UPDATE users SET line_id = 1 WHERE line_id IS NULL")
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
