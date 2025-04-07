import mysql.connector
import hashlib
from mysql.connector import Error

def init_database():
    try:
        # 连接MySQL服务器
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2'  # 请修改为实际的数据库密码
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS industry_db")
            cursor.execute("USE industry_db")
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(64) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 插入测试数据
            test_users = [
                ('admin', 'admin123', 'supervisor'),
                ('foreman1', 'foreman123', 'foreman'),
                ('worker1', 'worker123', 'member'),
                ('safety1', 'safety123', 'safety_officer')
            ]
            
            for username, password, role in test_users:
                # 对密码进行哈希处理
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # 检查用户是否已存在
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                        (username, hashed_password, role)
                    )
            
            connection.commit()
            print("数据库初始化完成")
            
    except Error as e:
        print(f"错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    init_database()