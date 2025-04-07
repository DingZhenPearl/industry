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
                    phone VARCHAR(20),
                    status ENUM('在岗', '请假', '离岗') DEFAULT '在岗',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 插入测试数据
            test_users = [
                ('admin', 'admin123', 'supervisor', '13800138000'),
                ('foreman1', 'foreman123', 'foreman', '13800138001'),
                ('worker1', 'worker123', 'member', '13800138002'),
                ('safety1', 'safety123', 'safety_officer', '13800138003')
            ]
            
            for username, password, role, phone in test_users:
                # 对密码进行哈希处理
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # 检查用户是否已存在
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO users (username, password, role, phone) VALUES (%s, %s, %s, %s)",
                        (username, hashed_password, role, phone)
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
