import sys
import json
import mysql.connector
from mysql.connector import Error
import argparse
import io
from datetime import datetime, date, timedelta

# 自定义JSON编码器，处理datetime类型
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

# 设置输出编码
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
# 工单表管理函数
# =============================================
def update_workorder_table_structure(connection=None):
    """更新工单表结构，添加新字段"""
    if connection is None:
        connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # 检查note字段是否存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'industry_db'
            AND table_name = 'workorders'
            AND column_name = 'note'
        """)

        if cursor.fetchone()[0] == 0:
            # 添加note字段
            cursor.execute("""
                ALTER TABLE workorders
                ADD COLUMN note TEXT COMMENT '完成报告' AFTER production_line
            """)
            connection.commit()
            print(json.dumps({
                'success': True,
                'message': '工单表结构更新成功，添加了note字段'
            }, ensure_ascii=False))
        else:
            print(json.dumps({
                'success': True,
                'message': '工单表结构已是最新的，note字段已存在'
            }, ensure_ascii=False))
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected() and cursor:
            cursor.close()

def create_workorder_table():
    """创建工单管理表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 检查表是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'industry_db'
            AND table_name = 'workorders'
        """)
        if cursor.fetchone()[0] > 0:
            print("工单表已存在")
            # 检查是否需要更新表结构
            update_workorder_table_structure(connection)
            return

        # 创建工单表
        cursor.execute("""
            CREATE TABLE workorders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                workorder_number VARCHAR(20) NOT NULL UNIQUE COMMENT '工单编号',
                task_type VARCHAR(20) NOT NULL COMMENT '任务类型',
                task_details TEXT COMMENT '任务详情',
                start_time DATETIME COMMENT '开始时间',
                deadline DATETIME COMMENT '截止时间',
                actual_end_time DATETIME COMMENT '实际结束时间',
                creator VARCHAR(50) COMMENT '发出人工号',
                status VARCHAR(20) NOT NULL DEFAULT '未接受' COMMENT '工单状态',
                foreman VARCHAR(50) COMMENT '负责工长工号',
                team VARCHAR(50) COMMENT '负责班组',
                team_members VARCHAR(100) COMMENT '负责组员工号',
                production_line VARCHAR(100) COMMENT '产线信息',
                note TEXT COMMENT '完成报告',
                extension_fields JSON COMMENT '扩展字段',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单管理表'
        """)

        print("工单表创建成功")
        connection.commit()

    except Error as e:
        print(f"创建工单表时出错: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def add_workorder(workorder_data):
    """添加新工单"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 生成工单编号 (如果没有提供)
        if 'workorder_number' not in workorder_data or not workorder_data['workorder_number']:
            # 生成格式: WO + 年月日 + 4位随机数
            now = datetime.now()
            date_part = now.strftime("%Y%m%d")

            # 获取当天最大工单号
            cursor.execute("""
                SELECT MAX(workorder_number) FROM workorders
                WHERE workorder_number LIKE %s
            """, (f"WO{date_part}%",))

            max_number = cursor.fetchone()[0]
            if max_number:
                # 提取序号部分并加1
                seq_number = int(max_number[-4:]) + 1
            else:
                seq_number = 1

            workorder_data['workorder_number'] = f"WO{date_part}{seq_number:04d}"

        # 处理日期时间字段
        datetime_fields = ['start_time', 'deadline', 'actual_end_time']
        for field in datetime_fields:
            if field in workorder_data and workorder_data[field]:
                workorder_data[field] = format_datetime(workorder_data[field])

        # 处理扩展字段 (如果有)
        if 'extension_fields' in workorder_data and isinstance(workorder_data['extension_fields'], dict):
            workorder_data['extension_fields'] = json.dumps(workorder_data['extension_fields'])

        # 构建插入语句
        fields = []
        placeholders = []
        values = []

        for key, value in workorder_data.items():
            if key != 'id':  # 跳过id字段，它是自增的
                fields.append(key)
                placeholders.append('%s')
                values.append(value)

        query = f"""
            INSERT INTO workorders ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '工单添加成功',
            'workorder_number': workorder_data['workorder_number']
        }, ensure_ascii=False))

    except Error as e:
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

def format_datetime(dt_str):
    """将ISO格式的日期时间字符串转换为MySQL兼容的格式"""
    if not dt_str:
        return None

    try:
        # 尝试解析ISO格式的日期时间
        if 'T' in dt_str:
            # 处理ISO格式：2023-04-12T01:28:41.571Z
            dt_str = dt_str.replace('Z', '')
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return dt_str
    except Exception as e:
        print(f"\n日期格式转换错误: {dt_str}, {str(e)}")
        return dt_str

def update_workorder(workorder_number, update_data):
    """更新工单信息"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 处理日期时间字段
        datetime_fields = ['start_time', 'deadline', 'actual_end_time']
        for field in datetime_fields:
            if field in update_data and update_data[field]:
                update_data[field] = format_datetime(update_data[field])

        # 处理扩展字段 (如果有)
        if 'extension_fields' in update_data and isinstance(update_data['extension_fields'], dict):
            update_data['extension_fields'] = json.dumps(update_data['extension_fields'])

        # 构建更新语句
        set_clause = []
        values = []

        for key, value in update_data.items():
            if key != 'workorder_number' and key != 'id':  # 跳过工单编号和id
                set_clause.append(f"{key} = %s")
                values.append(value)

        values.append(workorder_number)  # 添加WHERE条件的值

        query = f"""
            UPDATE workorders
            SET {', '.join(set_clause)}
            WHERE workorder_number = %s
        """

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount > 0:
            print(json.dumps({
                'success': True,
                'message': '工单更新成功',
                'workorder_number': workorder_number
            }, ensure_ascii=False))
        else:
            print(json.dumps({
                'success': False,
                'error': '未找到工单或无更改'
            }, ensure_ascii=False))

    except Error as e:
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



def get_workorder(workorder_number):
    """获取单个工单信息，并关联用户表获取用户名"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT w.*,
                   creator_u.username as creator_name,
                   foreman_u.username as foreman_name,
                   team_member_u.username as team_member_name
            FROM workorders w
            LEFT JOIN users creator_u ON w.creator = creator_u.employee_id
            LEFT JOIN users foreman_u ON w.foreman = foreman_u.employee_id
            LEFT JOIN users team_member_u ON w.team_members = team_member_u.employee_id
            WHERE w.workorder_number = %s
        """

        cursor.execute(query, (workorder_number,))
        workorder = cursor.fetchone()

        if workorder:
            # 处理JSON字段
            if 'extension_fields' in workorder and workorder['extension_fields']:
                try:
                    if isinstance(workorder['extension_fields'], str):
                        workorder['extension_fields'] = json.loads(workorder['extension_fields'])
                except:
                    pass  # 如果解析失败，保持原样

            print(json.dumps({
                'success': True,
                'data': workorder
            }, ensure_ascii=False, cls=DateTimeEncoder))
        else:
            print(json.dumps({
                'success': False,
                'error': '未找到工单'
            }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_workorders(filters=None):
    """获取工单列表，支持筛选，并关联用户表获取用户名"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 构建查询条件
        where_clause = []
        values = []

        if filters:
            for key, value in filters.items():
                if value:
                    if key == 'task_type':
                        where_clause.append(f"w.task_type = %s")
                        values.append(value)
                    elif key == 'task_types':
                        # 支持多个任务类型的查询
                        types = value.split(',')
                        placeholders = ', '.join(['%s'] * len(types))
                        where_clause.append(f"w.task_type IN ({placeholders})")
                        values.extend(types)
                    elif key == 'status':
                        where_clause.append(f"w.status = %s")
                        values.append(value)
                    elif key == 'foreman':
                        where_clause.append(f"w.foreman = %s")
                        values.append(value)
                    elif key == 'team':
                        where_clause.append(f"w.team = %s")
                        values.append(value)
                    elif key == 'production_line':
                        where_clause.append(f"w.production_line LIKE %s")
                        values.append(f"%{value}%")
                    elif key == 'creator':
                        where_clause.append(f"w.creator = %s")
                        values.append(value)
                    elif key == 'team_member':
                        where_clause.append(f"w.team_members LIKE %s")
                        values.append(f"%{value}%")
                    elif key == 'start_date':
                        where_clause.append(f"DATE(w.start_time) >= %s")
                        values.append(value)
                    elif key == 'end_date':
                        where_clause.append(f"DATE(w.start_time) <= %s")
                        values.append(value)
                    elif key == 'keyword':
                        where_clause.append(f"(w.task_details LIKE %s OR w.workorder_number LIKE %s)")
                        values.append(f"%{value}%")
                        values.append(f"%{value}%")

        # 构建完整查询，关联用户表获取用户名
        query = """
            SELECT w.*,
                   creator_u.username as creator_name,
                   foreman_u.username as foreman_name,
                   team_member_u.username as team_member_name
            FROM workorders w
            LEFT JOIN users creator_u ON w.creator = creator_u.employee_id
            LEFT JOIN users foreman_u ON w.foreman = foreman_u.employee_id
            LEFT JOIN users team_member_u ON w.team_members = team_member_u.employee_id
        """

        if where_clause:
            query += " WHERE " + " AND ".join(where_clause)

        query += " ORDER BY w.created_at DESC"

        cursor.execute(query, values)
        workorders = cursor.fetchall()

        # 处理JSON字段
        for workorder in workorders:
            if 'extension_fields' in workorder and workorder['extension_fields']:
                try:
                    if isinstance(workorder['extension_fields'], str):
                        workorder['extension_fields'] = json.loads(workorder['extension_fields'])
                except:
                    pass  # 如果解析失败，保持原样

        print(json.dumps({
            'success': True,
            'data': workorders
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def delete_workorder(workorder_number):
    """删除工单"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            DELETE FROM workorders
            WHERE workorder_number = %s
        """

        cursor.execute(query, (workorder_number,))
        connection.commit()

        if cursor.rowcount > 0:
            print(json.dumps({
                'success': True,
                'message': '工单删除成功',
                'workorder_number': workorder_number
            }, ensure_ascii=False))
        else:
            print(json.dumps({
                'success': False,
                'error': '未找到工单'
            }, ensure_ascii=False))

    except Error as e:
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

def get_workorder_stats():
    """获取工单统计信息"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 按状态统计
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM workorders
            GROUP BY status
        """)
        status_stats = cursor.fetchall()

        # 按类型统计
        cursor.execute("""
            SELECT task_type, COUNT(*) as count
            FROM workorders
            GROUP BY task_type
        """)
        type_stats = cursor.fetchall()

        # 按产线统计
        cursor.execute("""
            SELECT production_line, COUNT(*) as count
            FROM workorders
            WHERE production_line IS NOT NULL AND production_line != ''
            GROUP BY production_line
        """)
        line_stats = cursor.fetchall()

        # 按工长统计
        cursor.execute("""
            SELECT foreman, COUNT(*) as count
            FROM workorders
            WHERE foreman IS NOT NULL AND foreman != ''
            GROUP BY foreman
        """)
        foreman_stats = cursor.fetchall()

        # 总数统计
        cursor.execute("SELECT COUNT(*) as total FROM workorders")
        total = cursor.fetchone()['total']

        # 今日新增
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) as today_count
            FROM workorders
            WHERE DATE(created_at) = %s
        """, (today,))
        today_count = cursor.fetchone()['today_count']

        # 本周统计
        cursor.execute("""
            SELECT COUNT(*) as week_count
            FROM workorders
            WHERE YEARWEEK(created_at) = YEARWEEK(NOW())
        """)
        week_count = cursor.fetchone()['week_count']

        stats = {
            'total': total,
            'today_count': today_count,
            'week_count': week_count,
            'status_stats': status_stats,
            'type_stats': type_stats,
            'line_stats': line_stats,
            'foreman_stats': foreman_stats
        }

        print(json.dumps({
            'success': True,
            'data': stats
        }, ensure_ascii=False, cls=DateTimeEncoder))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# =============================================
# 主函数
# =============================================
def main():
    parser = argparse.ArgumentParser(description='工单管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 创建工单表命令
    create_table_parser = subparsers.add_parser('create-table', help='创建工单表')

    # 更新工单表结构命令
    update_table_parser = subparsers.add_parser('update-table', help='更新工单表结构')

    # 添加工单命令
    add_parser = subparsers.add_parser('add', help='添加工单')
    add_parser.add_argument('--data', required=True, help='工单数据(JSON格式)')

    # 更新工单命令
    update_parser = subparsers.add_parser('update', help='更新工单')
    update_parser.add_argument('--number', required=True, help='工单编号')
    update_parser.add_argument('--data', required=True, help='更新数据(JSON格式)')

    # 获取单个工单命令
    get_parser = subparsers.add_parser('get', help='获取工单')
    get_parser.add_argument('--number', required=True, help='工单编号')

    # 获取工单列表命令
    list_parser = subparsers.add_parser('list', help='获取工单列表')
    list_parser.add_argument('--type', help='任务类型')
    list_parser.add_argument('--types', help='多个任务类型，用逗号分隔')
    list_parser.add_argument('--status', help='工单状态')
    list_parser.add_argument('--foreman', help='负责工长')
    list_parser.add_argument('--team', help='负责班组')
    list_parser.add_argument('--line', help='产线信息')
    list_parser.add_argument('--creator', help='发出人')
    list_parser.add_argument('--team-member', help='负责组员')
    list_parser.add_argument('--start-date', help='开始日期')
    list_parser.add_argument('--end-date', help='结束日期')
    list_parser.add_argument('--keyword', help='关键词搜索')

    # 删除工单命令
    delete_parser = subparsers.add_parser('delete', help='删除工单')
    delete_parser.add_argument('--number', required=True, help='工单编号')

    # 获取工单统计信息命令
    stats_parser = subparsers.add_parser('stats', help='获取工单统计信息')

    args = parser.parse_args()

    # 根据命令执行相应的函数
    if args.command == 'create-table':
        create_workorder_table()
    elif args.command == 'update-table':
        update_workorder_table_structure()
    elif args.command == 'add':
        try:
            workorder_data = json.loads(args.data)
            add_workorder(workorder_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': '无效的JSON数据'
            }, ensure_ascii=False))
    elif args.command == 'update':
        try:
            update_data = json.loads(args.data)
            update_workorder(args.number, update_data)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'error': '无效的JSON数据'
            }, ensure_ascii=False))
    elif args.command == 'get':
        get_workorder(args.number)
    elif args.command == 'list':
        filters = {}
        if args.type:
            filters['task_type'] = args.type
        if args.types:
            filters['task_types'] = args.types
        if args.status:
            filters['status'] = args.status
        if args.foreman:
            filters['foreman'] = args.foreman
        if args.team:
            filters['team'] = args.team
        if args.line:
            filters['production_line'] = args.line
        if args.creator:
            filters['creator'] = args.creator
        if args.team_member:
            filters['team_member'] = args.team_member
        if args.start_date:
            filters['start_date'] = args.start_date
        if args.end_date:
            filters['end_date'] = args.end_date
        if args.keyword:
            filters['keyword'] = args.keyword
        get_workorders(filters)
    elif args.command == 'delete':
        delete_workorder(args.number)
    elif args.command == 'stats':
        get_workorder_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
