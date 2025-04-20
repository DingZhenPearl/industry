#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error
import argparse
import sys
import io
from datetime import datetime, date, timedelta

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 自定义 JSON 编码器，处理 datetime 和 date 对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

# 安全的 JSON 序列化函数
def safe_json_dumps(obj):
    return json.dumps(obj, ensure_ascii=False, cls=DateTimeEncoder)

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',  # 请根据实际情况修改密码
            database='industry_db',
            charset='utf8mb4',
            use_unicode=True
        )
        return connection
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'数据库连接失败: {str(e)}'
        }, ensure_ascii=False))
        exit(1)

def check_in(employee_id):
    """员工上班打卡"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取当前日期和时间
        now = datetime.now()
        today = now.date()

        # 检查今天是否已经打过卡
        cursor.execute("""
            SELECT * FROM attendance_records
            WHERE employee_id = %s AND date = %s
        """, (employee_id, today))

        record = cursor.fetchone()

        if record:
            # 如果已经打过卡，更新上班打卡时间
            if record['check_in_time'] is None:
                cursor.execute("""
                    UPDATE attendance_records
                    SET check_in_time = %s, updated_at = NOW()
                    WHERE id = %s
                """, (now, record['id']))

                # 更新用户状态为在岗
                cursor.execute("""
                    UPDATE users
                    SET status = '在岗'
                    WHERE employee_id = %s
                """, (employee_id,))

                connection.commit()

                print(json.dumps({
                    'success': True,
                    'message': '上班打卡成功',
                    'data': {
                        'check_in_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                        'date': today.strftime('%Y-%m-%d')
                    }
                }, ensure_ascii=False))
            else:
                print(json.dumps({
                    'success': False,
                    'error': '今天已经上班打卡'
                }, ensure_ascii=False))
        else:
            # 如果没有打过卡，创建新记录
            cursor.execute("""
                INSERT INTO attendance_records (employee_id, check_in_time, date)
                VALUES (%s, %s, %s)
            """, (employee_id, now, today))

            # 更新用户状态为在岗
            cursor.execute("""
                UPDATE users
                SET status = '在岗'
                WHERE employee_id = %s
            """, (employee_id,))

            connection.commit()

            print(json.dumps({
                'success': True,
                'message': '上班打卡成功',
                'data': {
                    'check_in_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'date': today.strftime('%Y-%m-%d')
                }
            }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'上班打卡失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def check_out(employee_id):
    """员工下班打卡"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取当前日期和时间
        now = datetime.now()
        today = now.date()

        # 检查今天是否已经打过上班卡
        cursor.execute("""
            SELECT * FROM attendance_records
            WHERE employee_id = %s AND date = %s
        """, (employee_id, today))

        record = cursor.fetchone()

        if record and record['check_in_time'] is not None:
            # 如果已经打过上班卡，更新下班打卡时间
            if record['check_out_time'] is None:
                cursor.execute("""
                    UPDATE attendance_records
                    SET check_out_time = %s, updated_at = NOW()
                    WHERE id = %s
                """, (now, record['id']))

                # 更新用户状态为离岗
                cursor.execute("""
                    UPDATE users
                    SET status = '离岗'
                    WHERE employee_id = %s
                """, (employee_id,))

                connection.commit()

                print(json.dumps({
                    'success': True,
                    'message': '下班打卡成功',
                    'data': {
                        'check_out_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                        'date': today.strftime('%Y-%m-%d')
                    }
                }, ensure_ascii=False))
            else:
                print(json.dumps({
                    'success': False,
                    'error': '今天已经下班打卡'
                }, ensure_ascii=False))
        else:
            print(json.dumps({
                'success': False,
                'error': '请先进行上班打卡'
            }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'下班打卡失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def submit_leave_request(employee_id, leave_type, start_date, end_date, reason):
    """提交请假申请"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 验证日期格式
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            if start > end:
                print(json.dumps({
                    'success': False,
                    'error': '开始日期不能晚于结束日期'
                }, ensure_ascii=False))
                return

            if start < date.today():
                print(json.dumps({
                    'success': False,
                    'error': '开始日期不能早于今天'
                }, ensure_ascii=False))
                return
        except ValueError:
            print(json.dumps({
                'success': False,
                'error': '日期格式无效，请使用YYYY-MM-DD格式'
            }, ensure_ascii=False))
            return

        # 验证请假类型
        valid_types = ['事假', '病假', '年假', '其他']
        if leave_type not in valid_types:
            print(json.dumps({
                'success': False,
                'error': f'请假类型无效，有效类型: {", ".join(valid_types)}'
            }, ensure_ascii=False))
            return

        # 插入请假记录
        cursor.execute("""
            INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, reason, status)
            VALUES (%s, %s, %s, %s, %s, '待审批')
        """, (employee_id, leave_type, start_date, end_date, reason))

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '请假申请提交成功，等待审批',
            'data': {
                'leave_id': cursor.lastrowid
            }
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'提交请假申请失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def approve_leave(leave_id, approver_id, approval_notes=''):
    """批准请假申请"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取请假记录
        cursor.execute("""
            SELECT * FROM leave_requests
            WHERE id = %s
        """, (leave_id,))

        leave_request = cursor.fetchone()

        if not leave_request:
            print(json.dumps({
                'success': False,
                'error': '请假记录不存在'
            }, ensure_ascii=False))
            return

        if leave_request['status'] != '待审批':
            print(json.dumps({
                'success': False,
                'error': f'请假记录状态为{leave_request["status"]}，无法审批'
            }, ensure_ascii=False))
            return

        # 更新请假记录状态
        cursor.execute("""
            UPDATE leave_requests
            SET status = '已批准', approver_id = %s, approval_time = NOW(), approval_notes = %s
            WHERE id = %s
        """, (approver_id, approval_notes, leave_id))

        # 更新用户状态为请假
        cursor.execute("""
            UPDATE users
            SET status = '请假'
            WHERE employee_id = %s
        """, (leave_request['employee_id'],))

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '请假申请已批准',
            'data': {
                'leave_id': leave_id,
                'employee_id': leave_request['employee_id'],
                'status': '已批准'
            }
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'批准请假申请失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def reject_leave(leave_id, approver_id, approval_notes=''):
    """拒绝请假申请"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取请假记录
        cursor.execute("""
            SELECT * FROM leave_requests
            WHERE id = %s
        """, (leave_id,))

        leave_request = cursor.fetchone()

        if not leave_request:
            print(json.dumps({
                'success': False,
                'error': '请假记录不存在'
            }, ensure_ascii=False))
            return

        if leave_request['status'] != '待审批':
            print(json.dumps({
                'success': False,
                'error': f'请假记录状态为{leave_request["status"]}，无法审批'
            }, ensure_ascii=False))
            return

        # 更新请假记录状态
        cursor.execute("""
            UPDATE leave_requests
            SET status = '已拒绝', approver_id = %s, approval_time = NOW(), approval_notes = %s
            WHERE id = %s
        """, (approver_id, approval_notes, leave_id))

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '请假申请已拒绝',
            'data': {
                'leave_id': leave_id,
                'employee_id': leave_request['employee_id'],
                'status': '已拒绝'
            }
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'拒绝请假申请失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def cancel_leave(leave_id, employee_id):
    """取消请假申请"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取请假记录
        cursor.execute("""
            SELECT * FROM leave_requests
            WHERE id = %s AND employee_id = %s
        """, (leave_id, employee_id))

        leave_request = cursor.fetchone()

        if not leave_request:
            print(json.dumps({
                'success': False,
                'error': '请假记录不存在或无权取消'
            }, ensure_ascii=False))
            return

        if leave_request['status'] not in ['待审批', '已批准']:
            print(json.dumps({
                'success': False,
                'error': f'请假记录状态为{leave_request["status"]}，无法取消'
            }, ensure_ascii=False))
            return

        # 更新请假记录状态
        cursor.execute("""
            UPDATE leave_requests
            SET status = '已取消', updated_at = NOW()
            WHERE id = %s
        """, (leave_id,))

        # 如果请假已批准且已经开始，则更新用户状态为在岗
        if leave_request['status'] == '已批准' and leave_request['start_date'] <= date.today():
            cursor.execute("""
                UPDATE users
                SET status = '在岗'
                WHERE employee_id = %s
            """, (employee_id,))

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '请假申请已取消',
            'data': {
                'leave_id': leave_id,
                'status': '已取消'
            }
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'取消请假申请失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_employee_attendance(employee_id, start_date=None, end_date=None):
    """获取员工考勤记录"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM attendance_records
            WHERE employee_id = %s
        """
        params = [employee_id]

        if start_date:
            query += " AND date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND date <= %s"
            params.append(end_date)

        query += " ORDER BY date DESC"

        cursor.execute(query, params)
        records = cursor.fetchall()

        # 处理日期和时间格式
        for record in records:
            if 'date' in record and record['date']:
                record['date'] = record['date'].strftime('%Y-%m-%d')
            if 'check_in_time' in record and record['check_in_time']:
                record['check_in_time'] = record['check_in_time'].strftime('%Y-%m-%d %H:%M:%S')
            if 'check_out_time' in record and record['check_out_time']:
                record['check_out_time'] = record['check_out_time'].strftime('%Y-%m-%d %H:%M:%S')
            if 'created_at' in record and record['created_at']:
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'updated_at' in record and record['updated_at']:
                record['updated_at'] = record['updated_at'].strftime('%Y-%m-%d %H:%M:%S')

        print(json.dumps({
            'success': True,
            'data': records
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取考勤记录失败: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_employee_leave_requests(employee_id, status=None):
    """获取员工请假记录"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM leave_requests
            WHERE employee_id = %s
        """
        params = [employee_id]

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        records = cursor.fetchall()

        # 处理日期和时间格式
        for record in records:
            if 'start_date' in record and record['start_date']:
                record['start_date'] = record['start_date'].strftime('%Y-%m-%d')
            if 'end_date' in record and record['end_date']:
                record['end_date'] = record['end_date'].strftime('%Y-%m-%d')
            if 'approval_time' in record and record['approval_time']:
                record['approval_time'] = record['approval_time'].strftime('%Y-%m-%d %H:%M:%S')
            if 'created_at' in record and record['created_at']:
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'updated_at' in record and record['updated_at']:
                record['updated_at'] = record['updated_at'].strftime('%Y-%m-%d %H:%M:%S')

        print(json.dumps({
            'success': True,
            'data': records
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取请假记录失败: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_pending_leave_requests(group_id=None, all_requests=False, approver_id=None):
    """获取待审批的请假申请"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT lr.*, u.username as employee_name, u.group_id, u.role
            FROM leave_requests lr
            JOIN users u ON lr.employee_id = u.employee_id
            WHERE lr.status = '待审批'
        """
        params = []

        # 如果是厂长，获取所有请假申请
        if all_requests:
            # 不添加组号限制，获取所有请假申请
            pass
        # 如果是工长或安全员，只获取其组内的请假申请，但不包括自己的请假申请
        elif group_id and group_id.strip():
            query += " AND u.group_id = %s"
            params.append(group_id)

            # 如果提供了审批人ID，排除审批人自己的请假申请
            if approver_id and approver_id.strip():
                query += " AND lr.employee_id != %s"
                params.append(approver_id)

        query += " ORDER BY lr.created_at ASC"

        cursor.execute(query, params)
        records = cursor.fetchall()

        # 处理日期和时间格式
        for record in records:
            if 'start_date' in record and record['start_date']:
                record['start_date'] = record['start_date'].strftime('%Y-%m-%d')
            if 'end_date' in record and record['end_date']:
                record['end_date'] = record['end_date'].strftime('%Y-%m-%d')
            if 'created_at' in record and record['created_at']:
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'updated_at' in record and record['updated_at']:
                record['updated_at'] = record['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'approval_time' in record and record['approval_time']:
                record['approval_time'] = record['approval_time'].strftime('%Y-%m-%d %H:%M:%S')

        print(safe_json_dumps({
            'success': True,
            'data': records
        }))

    except Error as e:
        print(safe_json_dumps({
            'success': False,
            'error': f'获取待审批请假申请失败: {str(e)}'
        }))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_employee_status(employee_id, status):
    """更新员工状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 验证状态
        valid_statuses = ['在岗', '离岗', '请假']
        if status not in valid_statuses:
            print(json.dumps({
                'success': False,
                'error': f'状态无效，有效状态: {", ".join(valid_statuses)}'
            }, ensure_ascii=False))
            return

        # 更新用户状态
        cursor.execute("""
            UPDATE users
            SET status = %s
            WHERE employee_id = %s
        """, (status, employee_id))

        connection.commit()

        print(json.dumps({
            'success': True,
            'message': '员工状态更新成功',
            'data': {
                'employee_id': employee_id,
                'status': status
            }
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'更新员工状态失败: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_processed_leave_requests(group_id=None, all_requests=False):
    """获取已处理的请假申请（已批准或已拒绝）"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT lr.*,
                   u.username as employee_name, u.group_id, u.role,
                   a.username as approver_name, a.role as approver_role
            FROM leave_requests lr
            JOIN users u ON lr.employee_id = u.employee_id
            LEFT JOIN users a ON lr.approver_id = a.employee_id
            WHERE lr.status IN ('已批准', '已拒绝')
        """
        params = []

        # 如果是厂长，获取所有已处理的请假申请
        if all_requests:
            # 不添加组号限制，获取所有已处理的请假申请
            pass
        # 如果是工长或安全员，只获取其组内的已处理的请假申请
        elif group_id and group_id.strip():
            query += " AND u.group_id = %s"
            params.append(group_id)

        query += " ORDER BY lr.approval_time DESC"

        cursor.execute(query, params)
        records = cursor.fetchall()

        # 处理日期和时间格式
        for record in records:
            if 'start_date' in record and record['start_date']:
                record['start_date'] = record['start_date'].strftime('%Y-%m-%d')
            if 'end_date' in record and record['end_date']:
                record['end_date'] = record['end_date'].strftime('%Y-%m-%d')
            if 'created_at' in record and record['created_at']:
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'updated_at' in record and record['updated_at']:
                record['updated_at'] = record['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'approval_time' in record and record['approval_time']:
                record['approval_time'] = record['approval_time'].strftime('%Y-%m-%d %H:%M:%S')

        print(safe_json_dumps({
            'success': True,
            'data': records
        }))

    except Error as e:
        print(safe_json_dumps({
            'success': False,
            'error': f'获取已处理请假申请失败: {str(e)}'
        }))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def get_today_attendance_status(employee_id):
    """获取员工今日考勤状态"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取当前日期
        today = date.today()

        # 查询今日考勤记录
        cursor.execute("""
            SELECT * FROM attendance_records
            WHERE employee_id = %s AND date = %s
        """, (employee_id, today))

        record = cursor.fetchone()

        # 查询用户状态
        cursor.execute("""
            SELECT status FROM users
            WHERE employee_id = %s
        """, (employee_id,))

        user_status = cursor.fetchone()

        result = {
            'date': today.strftime('%Y-%m-%d'),
            'has_checked_in': False,
            'has_checked_out': False,
            'check_in_time': None,
            'check_out_time': None,
            'status': user_status['status'] if user_status else 'unknown'
        }

        if record:
            result['has_checked_in'] = record['check_in_time'] is not None
            result['has_checked_out'] = record['check_out_time'] is not None

            if record['check_in_time']:
                result['check_in_time'] = record['check_in_time'].strftime('%Y-%m-%d %H:%M:%S')

            if record['check_out_time']:
                result['check_out_time'] = record['check_out_time'].strftime('%Y-%m-%d %H:%M:%S')

        print(json.dumps({
            'success': True,
            'data': result
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'获取今日考勤状态失败: {str(e)}'
        }, ensure_ascii=False))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='员工状态管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 上班打卡命令
    check_in_parser = subparsers.add_parser('check-in', help='上班打卡')
    check_in_parser.add_argument('employee_id', help='员工工号')

    # 下班打卡命令
    check_out_parser = subparsers.add_parser('check-out', help='下班打卡')
    check_out_parser.add_argument('employee_id', help='员工工号')

    # 提交请假申请命令
    leave_parser = subparsers.add_parser('submit-leave', help='提交请假申请')
    leave_parser.add_argument('employee_id', help='员工工号')
    leave_parser.add_argument('leave_type', help='请假类型')
    leave_parser.add_argument('start_date', help='开始日期')
    leave_parser.add_argument('end_date', help='结束日期')
    leave_parser.add_argument('reason', help='请假原因')

    # 批准请假申请命令
    approve_parser = subparsers.add_parser('approve-leave', help='批准请假申请')
    approve_parser.add_argument('leave_id', help='请假记录ID')
    approve_parser.add_argument('approver_id', help='审批人工号')
    approve_parser.add_argument('--notes', help='审批备注')

    # 拒绝请假申请命令
    reject_parser = subparsers.add_parser('reject-leave', help='拒绝请假申请')
    reject_parser.add_argument('leave_id', help='请假记录ID')
    reject_parser.add_argument('approver_id', help='审批人工号')
    reject_parser.add_argument('--notes', help='审批备注')

    # 取消请假申请命令
    cancel_parser = subparsers.add_parser('cancel-leave', help='取消请假申请')
    cancel_parser.add_argument('leave_id', help='请假记录ID')
    cancel_parser.add_argument('employee_id', help='员工工号')

    # 获取员工考勤记录命令
    attendance_parser = subparsers.add_parser('get-attendance', help='获取员工考勤记录')
    attendance_parser.add_argument('employee_id', help='员工工号')
    attendance_parser.add_argument('--start', help='开始日期')
    attendance_parser.add_argument('--end', help='结束日期')

    # 获取员工请假记录命令
    leave_records_parser = subparsers.add_parser('get-leave-records', help='获取员工请假记录')
    leave_records_parser.add_argument('employee_id', help='员工工号')
    leave_records_parser.add_argument('--status', help='请假状态')

    # 获取待审批的请假申请命令
    pending_parser = subparsers.add_parser('get-pending-leaves', help='获取待审批的请假申请')
    pending_parser.add_argument('--group-id', help='组号')
    pending_parser.add_argument('--all', action='store_true', help='获取所有请假申请（厂长权限）')
    pending_parser.add_argument('--approver-id', help='审批人工号，用于排除审批人自己的请假申请')

    # 获取已处理的请假申请命令
    processed_parser = subparsers.add_parser('get-processed-leaves', help='获取已处理的请假申请')
    processed_parser.add_argument('--group-id', help='组号')
    processed_parser.add_argument('--all', action='store_true', help='获取所有已处理的请假申请（厂长权限）')

    # 更新员工状态命令
    update_status_parser = subparsers.add_parser('update-status', help='更新员工状态')
    update_status_parser.add_argument('employee_id', help='员工工号')
    update_status_parser.add_argument('status', help='状态')

    # 获取员工今日考勤状态命令
    today_parser = subparsers.add_parser('get-today-status', help='获取员工今日考勤状态')
    today_parser.add_argument('employee_id', help='员工工号')

    args = parser.parse_args()

    if args.command == 'check-in':
        check_in(args.employee_id)
    elif args.command == 'check-out':
        check_out(args.employee_id)
    elif args.command == 'submit-leave':
        submit_leave_request(args.employee_id, args.leave_type, args.start_date, args.end_date, args.reason)
    elif args.command == 'approve-leave':
        approve_leave(args.leave_id, args.approver_id, args.notes or '')
    elif args.command == 'reject-leave':
        reject_leave(args.leave_id, args.approver_id, args.notes or '')
    elif args.command == 'cancel-leave':
        cancel_leave(args.leave_id, args.employee_id)
    elif args.command == 'get-attendance':
        get_employee_attendance(args.employee_id, args.start, args.end)
    elif args.command == 'get-leave-records':
        get_employee_leave_requests(args.employee_id, args.status)
    elif args.command == 'get-pending-leaves':
        get_pending_leave_requests(args.group_id, args.all, args.approver_id)
    elif args.command == 'get-processed-leaves':
        get_processed_leave_requests(args.group_id, args.all)
    elif args.command == 'update-status':
        update_employee_status(args.employee_id, args.status)
    elif args.command == 'get-today-status':
        get_today_attendance_status(args.employee_id)
    else:
        parser.print_help()
