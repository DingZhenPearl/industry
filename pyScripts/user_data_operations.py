import sys
import json
import hashlib
import mysql.connector
from mysql.connector import Error
import io
import argparse
import time
import random

# 在文件开头添加编码设置
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# =============================================
# 数据库连接函数
# =============================================
def get_db_connection():
    """创建并返回数据库连接"""
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

# =============================================
# 字段添加函数
# =============================================
def add_line_id_field():
    """添加line_id字段到users表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'industry_db'
            AND table_name = 'users'
            AND column_name = 'line_id'
        """)
        if cursor.fetchone()[0] == 0:
            # 添加line_id字段
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN line_id VARCHAR(50) DEFAULT '1' COMMENT '所属产线ID'
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
        cursor.execute("UPDATE users SET line_id = '1' WHERE line_id IS NULL")
        print(f"已更新 {cursor.rowcount} 条记录的默认产线")

        connection.commit()

    except Error as e:
        print(f"执行错误: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def add_machine_id_field():
    """添加machine_id字段到users表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'industry_db'
            AND table_name = 'users'
            AND column_name = 'machine_id'
        """)
        if cursor.fetchone()[0] == 0:
            # 添加machine_id字段
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN machine_id VARCHAR(50) NULL COMMENT '所属机器ID'
            """)
            print("成功添加machine_id字段")
        else:
            print("machine_id字段已存在")

        connection.commit()

    except Error as e:
        print(f"执行错误: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def add_employee_id_field():
    """添加employee_id字段到users表并为用户生成工号"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'industry_db'
            AND table_name = 'users'
            AND column_name = 'employee_id'
        """)
        if cursor.fetchone()[0] == 0:
            # 添加工号字段
            cursor.execute("ALTER TABLE users ADD employee_id VARCHAR(20) UNIQUE")
            print("成功添加employee_id字段")
        else:
            print("employee_id字段已存在")
            return

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
        print("工号生成并更新成功")

    except Exception as e:
        print(f"错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def add_group_id_field():
    """添加group_id字段到users表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'industry_db'
            AND table_name = 'users'
            AND column_name = 'group_id'
        """)
        if cursor.fetchone()[0] == 0:
            # 添加group_id字段
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN group_id INT NULL COMMENT '所属分组ID'
            """)
            print("成功添加group_id字段")
        else:
            print("group_id字段已存在")

        connection.commit()

    except Error as e:
        print(f"执行错误: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 数据迁移函数
# =============================================
def migrate_id_columns():
    """将line_id和machine_id从INT类型转换为VARCHAR类型"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        print("开始迁移数据库列类型...")

        # 检查line_id列类型
        cursor.execute("""
            SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'industry_db'
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'line_id'
        """)
        line_id_type = cursor.fetchone()

        # 检查machine_id列类型
        cursor.execute("""
            SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'industry_db'
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'machine_id'
        """)
        machine_id_type = cursor.fetchone()

        # 如果两个字段都已经是VARCHAR类型，则不需要迁移
        if (line_id_type and line_id_type[0] == 'varchar' and
            machine_id_type and machine_id_type[0] == 'varchar'):
            print("line_id和machine_id已经是VARCHAR类型，无需迁移")
            return

        # 1. 创建临时列并复制数据
        print("步骤1: 创建临时列并复制数据")
        if line_id_type and line_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users ADD COLUMN line_id_temp VARCHAR(50)")
            cursor.execute("UPDATE users SET line_id_temp = CAST(line_id AS CHAR) WHERE line_id IS NOT NULL")

        if machine_id_type and machine_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users ADD COLUMN machine_id_temp VARCHAR(50)")
            cursor.execute("UPDATE users SET machine_id_temp = CAST(machine_id AS CHAR) WHERE machine_id IS NOT NULL")

        # 2. 删除原列
        print("步骤2: 删除原INT类型列")
        if line_id_type and line_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users DROP COLUMN line_id")

        if machine_id_type and machine_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users DROP COLUMN machine_id")

        # 3. 重命名临时列为正式列
        print("步骤3: 重命名临时列为正式列")
        if line_id_type and line_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users CHANGE COLUMN line_id_temp line_id VARCHAR(50)")

        if machine_id_type and machine_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users CHANGE COLUMN machine_id_temp machine_id VARCHAR(50)")

        # 4. 添加注释
        print("步骤4: 添加列注释")
        if line_id_type and line_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users MODIFY COLUMN line_id VARCHAR(50) COMMENT '所属产线ID'")

        if machine_id_type and machine_id_type[0] != 'varchar':
            cursor.execute("ALTER TABLE users MODIFY COLUMN machine_id VARCHAR(50) COMMENT '所属机器ID'")

        connection.commit()
        print("迁移完成! line_id和machine_id已成功转换为VARCHAR(50)类型")

    except Error as e:
        print(f"迁移过程中出错: {e}")
        if connection:
            connection.rollback()
            print("已回滚所有更改")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")

# =============================================
# 验证函数
# =============================================
def verify_column_types():
    """验证line_id和machine_id列的数据类型是否为VARCHAR"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查询列信息
        query = """
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'industry_db'
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME IN ('line_id', 'machine_id')
        """

        cursor.execute(query)
        columns = cursor.fetchall()

        if not columns:
            print("未找到line_id或machine_id列")
            return

        print("列信息:")
        for col in columns:
            print(f"列名: {col['COLUMN_NAME']}")
            print(f"数据类型: {col['DATA_TYPE']}")
            print(f"列类型: {col['COLUMN_TYPE']}")
            print(f"注释: {col['COLUMN_COMMENT']}")
            print("-" * 30)

        # 查询示例数据
        cursor.execute("SELECT id, username, line_id, machine_id FROM users LIMIT 5")
        users = cursor.fetchall()

        print("\n用户数据示例:")
        for user in users:
            print(f"ID: {user['id']}, 用户名: {user['username']}")
            print(f"产线ID: {user['line_id']} (类型: {type(user['line_id']).__name__})")
            print(f"机器ID: {user['machine_id']} (类型: {type(user['machine_id']).__name__})")
            print("-" * 30)

    except Error as e:
        print(f"验证过程中出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")

# =============================================
# 数据获取函数
# =============================================
def get_users():
    """获取所有用户信息"""
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
                line_id,
                machine_id,
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
    """获取指定组的团队成员"""
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
                line_id,
                machine_id,
                COALESCE(status, 'active') as status,
                CASE
                    WHEN status = 'leave' THEN '请假'
                    WHEN status = 'task' THEN '任务中'
                    WHEN status = 'off' THEN '离岗'
                    ELSE '在岗'
                END as statusText
            FROM users
            WHERE group_id = %s
        """

        cursor.execute(query, (group_id,))
        members = cursor.fetchall()

        result = {
            'success': True,
            'data': members
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

def get_assigned_lines(group_id):
    """获取指定组号对应的产线列表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查询该组号对应的产线
        query = """
            SELECT DISTINCT line_id as id, line_id as name
            FROM users
            WHERE group_id = %s AND line_id IS NOT NULL
            ORDER BY line_id
        """

        cursor.execute(query, (group_id,))
        lines = cursor.fetchall()

        # 如果没有找到产线，添加默认产线
        if not lines:
            lines = [
                {'id': '1', 'name': '1'},
                {'id': '2', 'name': '2'},
                {'id': '3', 'name': '3'}
            ]

        result = {
            'success': True,
            'data': lines
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

# =============================================
# 用户验证函数
# =============================================
def verify_user(username, password, role):
    """验证用户登录信息（使用用户名）"""
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        check_query = """
            SELECT username, password, role, phone, employee_id, group_id, line_id, machine_id
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
                'group_id': user['group_id'],
                'line_id': user['line_id'],
                'machine_id': user['machine_id']
            }, ensure_ascii=False))
            return

        print(json.dumps({
            'authenticated': False,
            'error': '用户名或密码错误'
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            'authenticated': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def verify_user_by_id(employee_id, password, role):
    """验证用户登录信息（使用工号）"""
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        check_query = """
            SELECT username, password, role, phone, employee_id, group_id, line_id, machine_id
            FROM users WHERE employee_id = %s AND role = %s
        """
        cursor.execute(check_query, (employee_id, role))
        user = cursor.fetchone()

        if user and hashlib.sha256(password.encode()).hexdigest() == user['password']:
            print(json.dumps({
                'authenticated': True,
                'username': user['username'],
                'role': user['role'],
                'phone': user['phone'],
                'employee_id': user['employee_id'],
                'group_id': user['group_id'],
                'line_id': user['line_id'],
                'machine_id': user['machine_id']
            }, ensure_ascii=False))
            return

        print(json.dumps({
            'authenticated': False,
            'error': '工号或密码错误'
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            'authenticated': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def register(username, password, role):
    """注册新用户"""
    connection = None
    try:
        # 用户名现在由系统自动生成，不需要验证长度

        # 验证密码长度
        if len(password) < 6:
            print(json.dumps({
                'success': False,
                'error': '密码长度不能少于6个字符'
            }, ensure_ascii=False))
            return

        # 验证角色
        valid_roles = ['supervisor', 'foreman', 'member', 'safety_officer']
        if role not in valid_roles:
            print(json.dumps({
                'success': False,
                'error': '无效的角色类型'
            }, ensure_ascii=False))
            return

        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查用户名是否已存在，如果存在则修改用户名
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        if cursor.fetchone()[0] > 0:
            # 如果用户名已存在，添加随机数字后缀
            username = f"{username}_{int(time.time())}_{random.randint(1000, 9999)}"

        # 对密码进行哈希处理
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # 插入新用户
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
        """, (username, hashed_password, role))

        # 获取新用户ID
        user_id = cursor.lastrowid

        # 生成工号
        prefix = {
            'supervisor': 'SP',
            'foreman': 'FM',
            'member': 'WK',
            'safety_officer': 'SF'
        }.get(role, 'EMP')

        employee_id = f"{prefix}{user_id:04d}"

        # 更新工号
        cursor.execute("""
            UPDATE users SET employee_id = %s WHERE id = %s
        """, (employee_id, user_id))

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '注册成功',
            'user_id': user_id,
            'employee_id': employee_id
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_user(username, role, phone):
    """更新用户手机号"""
    connection = None
    try:
        # 验证手机号格式
        if not phone or len(phone) != 11 or not phone.isdigit():
            print(json.dumps({
                'success': False,
                'error': '请输入有效的11位手机号'
            }, ensure_ascii=False))
            return

        connection = get_db_connection()
        cursor = connection.cursor()

        update_query = "UPDATE users SET phone = %s WHERE username = %s AND role = %s"
        cursor.execute(update_query, (phone, username, role))
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '手机号更新成功'
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'手机号更新失败: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_username(current_username, role, new_username):
    """更新用户名"""
    connection = None
    try:
        # 验证新用户名长度
        if len(new_username) < 3 or len(new_username) > 20:
            print(json.dumps({
                'success': False,
                'error': '用户名长度应在3-20个字符之间'
            }, ensure_ascii=False))
            return

        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查新用户名是否已存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s AND username != %s",
                       (new_username, current_username))
        if cursor.fetchone()[0] > 0:
            print(json.dumps({
                'success': False,
                'error': '用户名已存在'
            }, ensure_ascii=False))
            return

        # 更新用户名
        cursor.execute("""
            UPDATE users SET username = %s
            WHERE username = %s AND role = %s
        """, (new_username, current_username, role))

        if cursor.rowcount == 0:
            print(json.dumps({
                'success': False,
                'error': '未找到用户或无权限修改'
            }, ensure_ascii=False))
            return

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '用户名更新成功',
            'new_username': new_username
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'用户名更新失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_password(username, role, new_password):
    """更新用户密码"""
    connection = None
    try:
        # 验证密码长度
        if len(new_password) < 6:
            print(json.dumps({
                'success': False,
                'error': '密码长度不能少于6个字符'
            }, ensure_ascii=False))
            return

        connection = get_db_connection()
        cursor = connection.cursor()

        # 对新密码进行哈希处理
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        # 更新密码
        cursor.execute("""
            UPDATE users SET password = %s
            WHERE username = %s AND role = %s
        """, (hashed_password, username, role))

        if cursor.rowcount == 0:
            print(json.dumps({
                'success': False,
                'error': '未找到用户或无权限修改'
            }, ensure_ascii=False))
            return

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '密码更新成功'
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'密码更新失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_group(username, role, group_id):
    """更新用户组号"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 更新组号
        cursor.execute("""
            UPDATE users SET group_id = %s
            WHERE username = %s AND role = %s
        """, (group_id, username, role))

        if cursor.rowcount == 0:
            print(json.dumps({
                'success': False,
                'error': '未找到用户或无权限修改'
            }, ensure_ascii=False))
            return

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '组号更新成功',
            'group_id': group_id
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'组号更新失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 初始化数据库函数
# =============================================
def init_database():
    """初始化数据库和表结构"""
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    group_id INT NULL COMMENT '所属分组ID',
                    line_id VARCHAR(50) NULL COMMENT '所属产线ID',
                    machine_id VARCHAR(50) NULL COMMENT '所属机器ID'
                )
            """)

            # 添加分组字段（如果表已存在且字段不存在）
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = 'industry_db'
                AND table_name = 'users'
                AND column_name = 'group_id'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users
                    ADD COLUMN group_id INT NULL COMMENT '所属分组ID'
                """)

            # 添加产线字段（如果表已存在且字段不存在）
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = 'industry_db'
                AND table_name = 'users'
                AND column_name = 'line_id'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users
                    ADD COLUMN line_id VARCHAR(50) NULL COMMENT '所属产线ID'
                """)

            # 添加机器字段（如果表已存在且字段不存在）
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_schema = 'industry_db'
                AND table_name = 'users'
                AND column_name = 'machine_id'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users
                    ADD COLUMN machine_id VARCHAR(50) NULL COMMENT '所属机器ID'
                """)

            # 插入测试数据
            test_users = [
                ('admin', 'admin123', 'supervisor', '13800138000', None),  # 厂长无需组号
                ('foreman1', 'foreman123', 'foreman', '13800138001', 1),   # 1号工长分配组号1
                ('foreman2', 'foreman123', 'foreman', '13800138005', 2),   # 2号工长分配组号2
                ('worker1', 'worker123', 'member', '13800138002', 1),      # 工人分配到1号组
                ('worker2', 'worker123', 'member', '13800138006', 2),      # 工人分配到2号组
                ('safety1', 'safety123', 'safety_officer', '13800138003', None)  # 安全员无需组号
            ]

            for username, password, role, phone, group_id in test_users:
                # 对密码进行哈希处理
                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                # 检查用户是否已存在
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if not cursor.fetchone():
                    # 插入新用户
                    cursor.execute("""
                        INSERT INTO users (username, password, role, phone, group_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (username, hashed_password, role, phone, group_id))

            connection.commit()
            print("数据库初始化完成")

    except Error as e:
        print(f"错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 主函数
# =============================================
def main():
    parser = argparse.ArgumentParser(description='数据库操作工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 初始化数据库命令
    init_parser = subparsers.add_parser('init', help='初始化数据库')

    # 添加字段命令
    add_field_parser = subparsers.add_parser('add-field', help='添加字段')
    add_field_parser.add_argument('field', choices=['line_id', 'machine_id', 'employee_id', 'group_id'],
                                 help='要添加的字段名')

    # 迁移命令
    migrate_parser = subparsers.add_parser('migrate', help='迁移数据类型')

    # 验证命令
    verify_parser = subparsers.add_parser('verify', help='验证列类型')

    # 获取用户命令
    get_users_parser = subparsers.add_parser('get-users', help='获取所有用户')

    # 获取团队成员命令
    get_team_parser = subparsers.add_parser('get-team', help='获取团队成员')
    get_team_parser.add_argument('group_id', help='组ID')

    # 获取产线命令
    get_lines_parser = subparsers.add_parser('get-lines', help='获取产线')
    get_lines_parser.add_argument('group_id', help='组ID')

    # 验证用户命令（使用用户名）
    verify_user_parser = subparsers.add_parser('verify-user', help='验证用户（使用用户名）')
    verify_user_parser.add_argument('username', help='用户名')
    verify_user_parser.add_argument('password', help='密码')
    verify_user_parser.add_argument('role', help='角色')

    # 验证用户命令（使用工号）
    verify_user_by_id_parser = subparsers.add_parser('verify-user-by-id', help='验证用户（使用工号）')
    verify_user_by_id_parser.add_argument('employee_id', help='工号')
    verify_user_by_id_parser.add_argument('password', help='密码')
    verify_user_by_id_parser.add_argument('role', help='角色')

    # 注册用户命令
    register_parser = subparsers.add_parser('register', help='注册新用户')
    register_parser.add_argument('username', help='用户名')
    register_parser.add_argument('password', help='密码')
    register_parser.add_argument('role', help='角色')

    # 更新用户名命令
    update_username_parser = subparsers.add_parser('update-username', help='更新用户名')
    update_username_parser.add_argument('current_username', help='当前用户名')
    update_username_parser.add_argument('role', help='角色')
    update_username_parser.add_argument('new_username', help='新用户名')

    # 更新密码命令
    update_password_parser = subparsers.add_parser('update-password', help='更新密码')
    update_password_parser.add_argument('username', help='用户名')
    update_password_parser.add_argument('role', help='角色')
    update_password_parser.add_argument('new_password', help='新密码')

    # 更新组号命令
    update_group_parser = subparsers.add_parser('update-group', help='更新组号')
    update_group_parser.add_argument('username', help='用户名')
    update_group_parser.add_argument('role', help='角色')
    update_group_parser.add_argument('group_id', help='组号')

    # 更新用户命令
    update_user_parser = subparsers.add_parser('update-user', help='更新用户')
    update_user_parser.add_argument('username', help='用户名')
    update_user_parser.add_argument('role', help='角色')
    update_user_parser.add_argument('phone', help='手机号')

    args = parser.parse_args()

    # 根据命令执行相应的函数
    if args.command == 'init':
        init_database()
    elif args.command == 'add-field':
        if args.field == 'line_id':
            add_line_id_field()
        elif args.field == 'machine_id':
            add_machine_id_field()
        elif args.field == 'employee_id':
            add_employee_id_field()
        elif args.field == 'group_id':
            add_group_id_field()
    elif args.command == 'migrate':
        migrate_id_columns()
    elif args.command == 'verify':
        verify_column_types()
    elif args.command == 'get-users':
        get_users()
    elif args.command == 'get-team':
        get_team_members(args.group_id)
    elif args.command == 'get-lines':
        get_assigned_lines(args.group_id)
    elif args.command == 'verify-user':
        verify_user(args.username, args.password, args.role)
    elif args.command == 'verify-user-by-id':
        verify_user_by_id(args.employee_id, args.password, args.role)
    elif args.command == 'update-user':
        update_user(args.username, args.role, args.phone)
    elif args.command == 'register':
        register(args.username, args.password, args.role)
    elif args.command == 'update-username':
        update_username(args.current_username, args.role, args.new_username)
    elif args.command == 'update-password':
        update_password(args.username, args.role, args.new_password)
    elif args.command == 'update-group':
        update_group(args.username, args.role, args.group_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
